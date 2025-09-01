# -*- coding: utf-8 -*-
"""
模型管理API
提供模型配置查看和切换功能
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
from loguru import logger

from config import settings, get_current_model_config
from models.model_adapter import ModelAdapterFactory, get_model_adapter, reset_model_adapter
from services.chat_service import ChatService

router = APIRouter(prefix="/api/models", tags=["模型管理"])

class ModelInfo(BaseModel):
    """模型信息"""
    provider: str
    model: str
    api_base: str
    is_configured: bool
    is_current: bool

class ModelSwitchRequest(BaseModel):
    """模型切换请求"""
    provider: str
    model: Optional[str] = None

class ModelTestRequest(BaseModel):
    """模型测试请求"""
    provider: str
    test_message: str = "你好，请简单介绍一下自己。"

class ModelTestResponse(BaseModel):
    """模型测试响应"""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    latency_ms: Optional[int] = None

@router.get("/supported", response_model=List[str])
async def get_supported_providers():
    """获取支持的模型提供商列表"""
    try:
        providers = ModelAdapterFactory.get_supported_providers()
        return providers
    except Exception as e:
        logger.error(f"获取支持的模型提供商失败: {e}")
        raise HTTPException(status_code=500, detail="获取支持的模型提供商失败")

@router.get("/current", response_model=Dict[str, Any])
async def get_current_model():
    """获取当前模型配置"""
    try:
        current_config = get_current_model_config()
        return {
            "provider": settings.model_provider,
            "config": current_config,
            "parameters": {
                "temperature": settings.temperature,
                "max_tokens": settings.max_tokens,
                "top_p": settings.top_p,
                "frequency_penalty": settings.frequency_penalty,
                "presence_penalty": settings.presence_penalty
            }
        }
    except Exception as e:
        logger.error(f"获取当前模型配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取当前模型配置失败")

@router.get("/list", response_model=List[ModelInfo])
async def list_models():
    """列出所有模型配置信息"""
    try:
        models = []
        
        # 模型配置映射
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
            }
        }
        
        for provider, config in model_configs.items():
            models.append(ModelInfo(
                provider=provider,
                model=config["model"],
                api_base=config["api_base"],
                is_configured=bool(config["api_key"]),
                is_current=(provider == settings.model_provider)
            ))
        
        return models
        
    except Exception as e:
        logger.error(f"列出模型配置失败: {e}")
        raise HTTPException(status_code=500, detail="列出模型配置失败")

@router.post("/switch")
async def switch_model(request: ModelSwitchRequest):
    """切换模型提供商"""
    try:
        # 验证提供商是否支持
        supported_providers = ModelAdapterFactory.get_supported_providers()
        if request.provider not in supported_providers:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的模型提供商: {request.provider}"
            )
        
        # 更新环境变量（临时）
        os.environ["MODEL_PROVIDER"] = request.provider
        if request.model:
            os.environ[f"{request.provider.upper()}_MODEL"] = request.model
        
        # 重新加载配置
        settings.model_provider = request.provider
        
        # 重置模型适配器
        reset_model_adapter()
        
        # 验证新配置
        try:
            adapter = get_model_adapter()
            logger.info(f"成功切换到模型提供商: {request.provider}")
        except Exception as e:
            # 恢复原配置
            os.environ["MODEL_PROVIDER"] = settings.model_provider
            raise HTTPException(
                status_code=400,
                detail=f"切换模型失败，配置无效: {str(e)}"
            )
        
        return {
            "success": True,
            "message": f"成功切换到 {request.provider}",
            "current_provider": request.provider
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换模型失败: {e}")
        raise HTTPException(status_code=500, detail="切换模型失败")

@router.post("/test", response_model=ModelTestResponse)
async def test_model(request: ModelTestRequest):
    """测试模型连接和响应"""
    import time
    
    try:
        # 临时切换到指定提供商进行测试
        original_provider = settings.model_provider
        
        try:
            # 临时设置
            os.environ["MODEL_PROVIDER"] = request.provider
            settings.model_provider = request.provider
            
            # 创建测试适配器
            reset_model_adapter()
            adapter = get_model_adapter()
            
            # 构建测试消息
            messages = [
                {"role": "system", "content": "你是一个智能助手，请简洁地回答用户问题。"},
                {"role": "user", "content": request.test_message}
            ]
            
            # 记录开始时间
            start_time = time.time()
            
            # 调用模型
            response = adapter.chat_completion(messages, max_tokens=100)
            
            # 计算延迟
            latency_ms = int((time.time() - start_time) * 1000)
            
            return ModelTestResponse(
                success=True,
                response=response,
                latency_ms=latency_ms
            )
            
        finally:
            # 恢复原配置
            os.environ["MODEL_PROVIDER"] = original_provider
            settings.model_provider = original_provider
            reset_model_adapter()
            
    except Exception as e:
        logger.error(f"测试模型 {request.provider} 失败: {e}")
        return ModelTestResponse(
            success=False,
            error=str(e)
        )

@router.get("/status")
async def get_model_status():
    """获取模型状态信息"""
    try:
        # 获取当前适配器
        adapter = get_model_adapter()
        
        # 检查配置有效性
        is_valid = adapter.validate_config()
        
        return {
            "provider": settings.model_provider,
            "model": adapter.model,
            "api_base": adapter.api_base,
            "is_configured": is_valid,
            "status": "ready" if is_valid else "not_configured"
        }
        
    except Exception as e:
        logger.error(f"获取模型状态失败: {e}")
        return {
            "provider": settings.model_provider,
            "status": "error",
            "error": str(e)
        }

@router.get("/providers/{provider}/models")
async def get_provider_models(provider: str):
    """获取指定提供商的可用模型列表"""
    # 预定义的模型列表
    provider_models = {
        "openai": [
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k", 
            "gpt-4-turbo-preview", "gpt-4-vision-preview"
        ],
        "gemini": [
            "gemini-pro", "gemini-pro-vision"
        ],
        "deepseek": [
            "deepseek-chat", "deepseek-coder"
        ],
        "zhipu": [
            "glm-4", "glm-4v", "glm-3-turbo"
        ],
        "baichuan": [
            "Baichuan2-Turbo", "Baichuan2-Turbo-192k"
        ],
        "qwen": [
            "qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext"
        ],
        "moonshot": [
            "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"
        ],
        "yi": [
            "yi-34b-chat-0205", "yi-34b-chat-200k", "yi-vl-plus"
        ]
    }
    
    if provider not in provider_models:
        raise HTTPException(status_code=404, detail=f"不支持的提供商: {provider}")
    
    return {
        "provider": provider,
        "models": provider_models[provider]
    }