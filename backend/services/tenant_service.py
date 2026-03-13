#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
租户管理服务
用于多租户隔离：模型配置、知识库、策略、会话等
"""

import os
import json
import uuid
from typing import Dict, Any, Optional

from loguru import logger


class TenantService:
    """租户管理服务"""

    def __init__(self):
        self.base_dir = "./data/tenants"
        self.index_file = os.path.join(self.base_dir, "tenants.json")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        os.makedirs(self.base_dir, exist_ok=True)
        if not os.path.exists(self.index_file):
            with open(self.index_file, "w", encoding="utf-8") as file:
                json.dump({"tenants": {}}, file, ensure_ascii=False, indent=2)

    def _load_index(self) -> Dict[str, Any]:
        try:
            with open(self.index_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"加载租户索引失败: {e}")
            return {"tenants": {}}

    def _save_index(self, data: Dict[str, Any]) -> None:
        with open(self.index_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def create_tenant(self, name: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        index = self._load_index()
        tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
        key = api_key or f"tk_{uuid.uuid4().hex}"

        index["tenants"][tenant_id] = {
            "name": name,
            "api_key": key
        }
        self._save_index(index)

        self._ensure_tenant_dirs(tenant_id)

        return {
            "tenant_id": tenant_id,
            "api_key": key,
            "name": name
        }

    def list_tenants(self) -> Dict[str, Any]:
        index = self._load_index()
        tenants = []
        for tenant_id, tenant in index.get("tenants", {}).items():
            tenants.append({
                "tenant_id": tenant_id,
                "name": tenant.get("name"),
                "api_key": tenant.get("api_key")
            })
        return {"tenants": tenants}

    def reset_api_key(self, tenant_id: str) -> Dict[str, Any]:
        index = self._load_index()
        tenant = index.get("tenants", {}).get(tenant_id)
        if not tenant:
            raise ValueError("租户不存在")
        new_key = f"tk_{uuid.uuid4().hex}"
        tenant["api_key"] = new_key
        index["tenants"][tenant_id] = tenant
        self._save_index(index)
        return {"tenant_id": tenant_id, "api_key": new_key}

    def update_api_key(self, tenant_id: str, api_key: str) -> Dict[str, Any]:
        index = self._load_index()
        tenant = index.get("tenants", {}).get(tenant_id)
        if not tenant:
            raise ValueError("租户不存在")
        tenant["api_key"] = api_key
        index["tenants"][tenant_id] = tenant
        self._save_index(index)
        return {"tenant_id": tenant_id, "api_key": api_key}

    def _ensure_tenant_dirs(self, tenant_id: str) -> None:
        base = self.get_tenant_base_dir(tenant_id)
        os.makedirs(base, exist_ok=True)
        os.makedirs(os.path.join(base, "knowledge"), exist_ok=True)
        os.makedirs(os.path.join(base, "memory"), exist_ok=True)
        os.makedirs(os.path.join(base, "policy"), exist_ok=True)

    def get_tenant_by_key(self, api_key: str) -> Optional[str]:
        index = self._load_index()
        for tenant_id, tenant in index.get("tenants", {}).items():
            if tenant.get("api_key") == api_key:
                return tenant_id
        return None

    def get_tenant_base_dir(self, tenant_id: str) -> str:
        return os.path.join(self.base_dir, tenant_id)

    def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        config_file = os.path.join(self.get_tenant_base_dir(tenant_id), "config.json")
        if not os.path.exists(config_file):
            return {}
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"读取租户配置失败: {e}")
            return {}

    def update_tenant_config(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_tenant_dirs(tenant_id)
        current = self.get_tenant_config(tenant_id)
        merged = self._deep_merge(current, updates)
        config_file = os.path.join(self.get_tenant_base_dir(tenant_id), "config.json")
        with open(config_file, "w", encoding="utf-8") as file:
            json.dump(merged, file, ensure_ascii=False, indent=2)
        return merged

    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                base[key] = self._deep_merge(base.get(key, {}), value)
            else:
                base[key] = value
        return base
