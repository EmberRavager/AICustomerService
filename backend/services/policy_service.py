#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略配置服务
用于管理自动发货、意图路由、风控与人工接管策略
"""

import json
import os
from typing import Dict, Any, Optional

from loguru import logger

from config import get_settings


class PolicyService:
    """策略配置服务"""

    def __init__(self, tenant_id: Optional[str] = None):
        self.settings = get_settings()
        base_dir = "./data"
        if tenant_id:
            base_dir = os.path.join(base_dir, "tenants", tenant_id)
        self.data_dir = os.path.join(base_dir, "policy")
        self.policy_file = os.path.join(self.data_dir, "policy.json")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.policy_file):
            legacy_file = "./data/policy.json"
            if os.path.exists(legacy_file):
                try:
                    with open(legacy_file, "r", encoding="utf-8") as file:
                        legacy_data = json.load(file)
                    self._save_policy(legacy_data)
                    return
                except Exception:
                    pass
            self._save_policy(self._default_policy())

    def _default_policy(self) -> Dict[str, Any]:
        return {
            "auto_ship": {
                "enabled": self.settings.auto_ship_enabled,
                "reply_text": self.settings.auto_ship_reply,
                "trigger_status": ["paid", "wait_seller_ship", "等待卖家发货"]
            },
            "intent_routing": {
                "price_keywords": ["便宜", "价", "砍价", "少点", "优惠"],
                "price_patterns": ["\\d+元", "能少\\d+"],
                "tech_keywords": ["参数", "规格", "型号", "连接", "对比"],
                "tech_patterns": ["和.+比"]
            },
            "risk_guard": {
                "enabled": True,
                "blocked_keywords": ["微信", "QQ", "支付宝", "银行卡", "线下"],
                "reply_text": "[安全提醒]请通过平台沟通，避免私下交易风险。"
            },
            "manual_takeover": {
                "enabled": True,
                "session_ids": []
            }
        }

    def _load_policy(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self.policy_file):
                return self._default_policy()
            with open(self.policy_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"加载策略配置失败: {e}")
            return self._default_policy()

    def _save_policy(self, policy: Dict[str, Any]) -> None:
        with open(self.policy_file, "w", encoding="utf-8") as file:
            json.dump(policy, file, ensure_ascii=False, indent=2)

    def get_policy(self) -> Dict[str, Any]:
        return self._load_policy()

    def update_policy(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        policy = self._load_policy()
        merged = self._deep_merge(policy, updates)
        self._save_policy(merged)
        return merged

    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                base[key] = self._deep_merge(base.get(key, {}), value)
            else:
                base[key] = value
        return base
