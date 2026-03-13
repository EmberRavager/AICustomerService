#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统配置模块
管理环境变量和系统配置
"""

import os
import json
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    """系统配置类"""
    
    # 模型提供商配置
    model_provider: str = os.getenv("MODEL_PROVIDER", "qwen")  # openai, gemini, deepseek, zhipu, baichuan, qwen
    
    # OpenAI配置
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_api_base: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Google Gemini配置
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    gemini_api_base: str = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com")
    
    # DeepSeek配置
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_api_base: str = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # 智谱AI配置
    zhipu_api_key: str = os.getenv("ZHIPU_API_KEY", "")
    zhipu_api_base: str = os.getenv("ZHIPU_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
    zhipu_model: str = os.getenv("ZHIPU_MODEL", "glm-4")
    
    # 百川智能配置
    baichuan_api_key: str = os.getenv("BAICHUAN_API_KEY", "")
    baichuan_api_base: str = os.getenv("BAICHUAN_API_BASE", "https://api.baichuan-ai.com/v1")
    baichuan_model: str = os.getenv("BAICHUAN_MODEL", "Baichuan2-Turbo")
    
    # 通义千问配置
    qwen_api_key: str = os.getenv("QWEN_API_KEY", "")
    qwen_api_base: str = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/api/v1")
    qwen_model: str = os.getenv("QWEN_MODEL", "qwen-turbo")
    
    # 月之暗面配置
    moonshot_api_key: str = os.getenv("MOONSHOT_API_KEY", "")
    moonshot_api_base: str = os.getenv("MOONSHOT_API_BASE", "https://api.moonshot.cn/v1")
    moonshot_model: str = os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k")
    
    # 零一万物配置
    yi_api_key: str = os.getenv("YI_API_KEY", "")
    yi_api_base: str = os.getenv("YI_API_BASE", "https://api.lingyiwanwu.com/v1")
    yi_model: str = os.getenv("YI_MODEL", "yi-34b-chat-0205")

    # OpenRouter配置
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_api_base: str = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    openrouter_referer: str = os.getenv("OPENROUTER_REFERER", "")
    openrouter_title: str = os.getenv("OPENROUTER_TITLE", "")
    openrouter_headers: str = os.getenv("OPENROUTER_HEADERS", "")

    # 自定义OpenAI兼容配置
    custom_api_key: str = os.getenv("CUSTOM_API_KEY", "")
    custom_api_base: str = os.getenv("CUSTOM_API_BASE", "")
    custom_model: str = os.getenv("CUSTOM_MODEL", "")
    custom_headers: str = os.getenv("CUSTOM_HEADERS", "")

    # 管理员认证配置
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))
    
    # 通用模型配置
    default_model: str = os.getenv("DEFAULT_MODEL", "qwen-turbo")
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    top_p: float = float(os.getenv("TOP_P", "1.0"))
    frequency_penalty: float = float(os.getenv("FREQUENCY_PENALTY", "0.0"))
    presence_penalty: float = float(os.getenv("PRESENCE_PENALTY", "0.0"))
    
    # 向量数据库配置
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")

    # 闲鱼商品接口配置
    xianyu_api_base: str = os.getenv("XIAN_YU_API_BASE", "https://h5api.m.goofish.com")
    xianyu_app_key: str = os.getenv("XIAN_YU_APP_KEY", "34839810")
    xianyu_cookies: str = os.getenv("XIAN_YU_COOKIES", "")

    # 自动发货配置（虚拟交易）
    auto_ship_enabled: bool = os.getenv("AUTO_SHIP_ENABLED", "True").lower() == "true"
    auto_ship_reply: str = os.getenv(
        "AUTO_SHIP_REPLY",
        "已为您安排自动发货，请稍等 1-3 分钟完成交付。如有问题随时联系。"
    )
    
    # 系统提示词
    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT", 
        "你是一个专业的智能客服助手，请用友好、专业的语气回答用户的问题。"
    )
    
    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    # 服务器配置
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"

    # CORS 和安全配置
    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:1111,http://127.0.0.1:1111"
    )
    allowed_hosts: str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    def get_allowed_origins(self) -> list:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def get_allowed_hosts(self) -> list:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

# 创建全局配置实例
settings = Settings()

def get_settings() -> Settings:
    """获取配置实例"""
    return settings

def validate_config() -> bool:
    """验证配置是否有效"""
    try:
        # 验证模型提供商配置
        provider_configs = {
            "openai": settings.openai_api_key,
            "gemini": settings.gemini_api_key,
            "deepseek": settings.deepseek_api_key,
            "zhipu": settings.zhipu_api_key,
            "baichuan": settings.baichuan_api_key,
            "qwen": settings.qwen_api_key,
            "moonshot": settings.moonshot_api_key,
            "yi": settings.yi_api_key,
            "openrouter": settings.openrouter_api_key,
            "custom": settings.custom_api_key
        }
        
        if settings.model_provider not in provider_configs:
            raise ValueError(f"不支持的模型提供商: {settings.model_provider}")
        
        api_key = provider_configs[settings.model_provider]
        if not api_key:
            raise ValueError(f"{settings.model_provider.upper()} API Key未配置")
        
        # 创建必要的目录
        os.makedirs(os.path.dirname(settings.chroma_persist_directory), exist_ok=True)
        os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
        
        return True
    except Exception as e:
        print(f"配置验证失败: {e}")
        return False

def get_current_model_config() -> dict:
    """获取当前模型提供商的配置"""
    def parse_headers(raw_value: str) -> dict:
        if not raw_value:
            return {}
        try:
            parsed = json.loads(raw_value)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}
        return {}

    model_configs = {
        "openai": {
            "api_key": settings.openai_api_key,
            "api_base": settings.openai_api_base,
            "model": settings.openai_model
        },
        "gemini": {
            "api_key": settings.gemini_api_key,
            "api_base": settings.gemini_api_base,
            "model": settings.gemini_model
        },
        "deepseek": {
            "api_key": settings.deepseek_api_key,
            "api_base": settings.deepseek_api_base,
            "model": settings.deepseek_model
        },
        "zhipu": {
            "api_key": settings.zhipu_api_key,
            "api_base": settings.zhipu_api_base,
            "model": settings.zhipu_model
        },
        "baichuan": {
            "api_key": settings.baichuan_api_key,
            "api_base": settings.baichuan_api_base,
            "model": settings.baichuan_model
        },
        "qwen": {
            "api_key": settings.qwen_api_key,
            "api_base": settings.qwen_api_base,
            "model": settings.qwen_model
        },
        "moonshot": {
            "api_key": settings.moonshot_api_key,
            "api_base": settings.moonshot_api_base,
            "model": settings.moonshot_model
        },
        "yi": {
            "api_key": settings.yi_api_key,
            "api_base": settings.yi_api_base,
            "model": settings.yi_model
        },
        "openrouter": {
            "api_key": settings.openrouter_api_key,
            "api_base": settings.openrouter_api_base,
            "model": settings.openrouter_model,
            "referer": settings.openrouter_referer,
            "title": settings.openrouter_title,
            "headers": parse_headers(settings.openrouter_headers)
        },
        "custom": {
            "api_key": settings.custom_api_key,
            "api_base": settings.custom_api_base,
            "model": settings.custom_model,
            "headers": parse_headers(settings.custom_headers)
        }
    }
    
    return model_configs.get(settings.model_provider, {})
