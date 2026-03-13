#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闲鱼商品信息服务
通过闲鱼 H5 API 获取商品详情数据
"""

import hashlib
import json
import time
from typing import Dict, Any

import requests
from loguru import logger

from config import get_settings


class XianyuService:
    """闲鱼商品信息服务"""

    def __init__(self):
        settings = get_settings()
        self.api_base = settings.xianyu_api_base
        self.app_key = settings.xianyu_app_key
        self.cookies_str = settings.xianyu_cookies

        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.goofish.com",
            "referer": "https://www.goofish.com/",
            "user-agent": "Mozilla/5.0"
        })

        if self.cookies_str:
            self._load_cookies(self.cookies_str)

    def _load_cookies(self, cookies_str: str) -> None:
        """加载 Cookie 字符串到会话"""
        jar = requests.cookies.RequestsCookieJar()
        for part in cookies_str.split(";"):
            part = part.strip()
            if not part or "=" not in part:
                continue
            name, value = part.split("=", 1)
            jar.set(name, value, domain=".goofish.com")
        self.session.cookies = jar

    def _get_token(self) -> str:
        """从 Cookie 中提取 token"""
        token_cookie = self.session.cookies.get("_m_h5_tk", "")
        if not token_cookie:
            raise ValueError("未配置可用的闲鱼 Cookie（缺少 _m_h5_tk）")
        return token_cookie.split("_")[0]

    def _sign(self, timestamp: str, token: str, data_str: str) -> str:
        """生成签名"""
        raw = f"{token}&{timestamp}&{self.app_key}&{data_str}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def get_item_info(self, item_id: str) -> Dict[str, Any]:
        """获取商品信息"""
        if not self.cookies_str:
            raise ValueError("未配置闲鱼 Cookie，无法调用商品接口")

        timestamp = str(int(time.time() * 1000))
        data_str = json.dumps({"itemId": str(item_id)}, separators=(",", ":"))
        token = self._get_token()
        sign = self._sign(timestamp, token, data_str)

        params = {
            "jsv": "2.7.2",
            "appKey": self.app_key,
            "t": timestamp,
            "sign": sign,
            "v": "1.0",
            "type": "originaljson",
            "dataType": "json",
            "api": "mtop.taobao.idle.pc.detail",
            "sessionOption": "AutoLoginOnly"
        }
        payload = {"data": data_str}

        url = f"{self.api_base}/h5/mtop.taobao.idle.pc.detail/1.0/"
        response = self.session.post(url, params=params, data=payload, timeout=20)
        response.raise_for_status()

        body = response.json()
        ret = body.get("ret", [])
        if not any("SUCCESS" in r for r in ret):
            raise ValueError(f"闲鱼接口返回异常: {ret}")

        logger.debug(f"闲鱼商品信息获取成功: {item_id}")
        return body
