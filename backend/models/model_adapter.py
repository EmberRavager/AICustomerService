# -*- coding: utf-8 -*-
"""
多模型适配器
统一处理不同AI模型提供商的接口
"""

import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import openai
import requests
import json
from config import settings, get_current_model_config

logger = logging.getLogger(__name__)

class BaseModelAdapter(ABC):
    """模型适配器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("api_key")
        self.api_base = config.get("api_base")
        self.model = config.get("model")
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天完成接口"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置"""
        pass

class OpenAIAdapter(BaseModelAdapter):
    """OpenAI模型适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        openai.api_key = self.api_key
        openai.api_base = self.api_base
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """OpenAI聊天完成"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", settings.temperature),
                max_tokens=kwargs.get("max_tokens", settings.max_tokens),
                top_p=kwargs.get("top_p", settings.top_p),
                frequency_penalty=kwargs.get("frequency_penalty", settings.frequency_penalty),
                presence_penalty=kwargs.get("presence_penalty", settings.presence_penalty)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    def validate_config(self) -> bool:
        """验证OpenAI配置"""
        return bool(self.api_key and self.model)

class GeminiAdapter(BaseModelAdapter):
    """Google Gemini模型适配器"""
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Gemini聊天完成"""
        try:
            # 转换消息格式
            prompt = self._convert_messages_to_prompt(messages)
            
            url = f"{self.api_base}/v1beta/models/{self.model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": kwargs.get("temperature", settings.temperature),
                    "maxOutputTokens": kwargs.get("max_tokens", settings.max_tokens),
                    "topP": kwargs.get("top_p", settings.top_p)
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
            
        except Exception as e:
            logger.error(f"Gemini API调用失败: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """将消息转换为Gemini格式的提示"""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n\n".join(prompt_parts)
    
    def validate_config(self) -> bool:
        """验证Gemini配置"""
        return bool(self.api_key and self.model)

class DeepSeekAdapter(BaseModelAdapter):
    """DeepSeek模型适配器"""
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """DeepSeek聊天完成"""
        try:
            url = f"{self.api_base}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", settings.temperature),
                "max_tokens": kwargs.get("max_tokens", settings.max_tokens),
                "top_p": kwargs.get("top_p", settings.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", settings.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", settings.presence_penalty)
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise
    
    def validate_config(self) -> bool:
        """验证DeepSeek配置"""
        return bool(self.api_key and self.model)

class ZhipuAdapter(BaseModelAdapter):
    """智谱AI模型适配器"""
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """智谱AI聊天完成"""
        try:
            url = f"{self.api_base}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", settings.temperature),
                "max_tokens": kwargs.get("max_tokens", settings.max_tokens),
                "top_p": kwargs.get("top_p", settings.top_p)
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"智谱AI API调用失败: {e}")
            raise
    
    def validate_config(self) -> bool:
        """验证智谱AI配置"""
        return bool(self.api_key and self.model)

class BaichuanAdapter(BaseModelAdapter):
    """百川智能模型适配器"""
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """百川智能聊天完成"""
        try:
            url = f"{self.api_base}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", settings.temperature),
                "max_tokens": kwargs.get("max_tokens", settings.max_tokens),
                "top_p": kwargs.get("top_p", settings.top_p)
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"百川智能 API调用失败: {e}")
            raise
    
    def validate_config(self) -> bool:
        """验证百川智能配置"""
        return bool(self.api_key and self.model)

class QwenAdapter(BaseModelAdapter):
    """通义千问模型适配器"""
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """通义千问聊天完成"""
        try:
            url = f"{self.api_base}/services/aigc/text-generation/generation"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 转换消息格式
            prompt = self._convert_messages_to_prompt(messages)
            
            data = {
                "model": self.model,
                "input": {
                    "prompt": prompt
                },
                "parameters": {
                    "temperature": kwargs.get("temperature", settings.temperature),
                    "max_tokens": kwargs.get("max_tokens", settings.max_tokens),
                    "top_p": kwargs.get("top_p", settings.top_p)
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["output"]["text"]
            
        except Exception as e:
            logger.error(f"通义千问 API调用失败: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """将消息转换为通义千问格式的提示"""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"系统: {content}")
            elif role == "user":
                prompt_parts.append(f"用户: {content}")
            elif role == "assistant":
                prompt_parts.append(f"助手: {content}")
        return "\n\n".join(prompt_parts)
    
    def validate_config(self) -> bool:
        """验证通义千问配置"""
        return bool(self.api_key and self.model)

class MoonshotAdapter(BaseModelAdapter):
    """月之暗面模型适配器"""
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """月之暗面聊天完成"""
        try:
            url = f"{self.api_base}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", settings.temperature),
                "max_tokens": kwargs.get("max_tokens", settings.max_tokens),
                "top_p": kwargs.get("top_p", settings.top_p)
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"月之暗面 API调用失败: {e}")
            raise
    
    def validate_config(self) -> bool:
        """验证月之暗面配置"""
        return bool(self.api_key and self.model)

class YiAdapter(BaseModelAdapter):
    """零一万物模型适配器"""
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """零一万物聊天完成"""
        try:
            url = f"{self.api_base}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", settings.temperature),
                "max_tokens": kwargs.get("max_tokens", settings.max_tokens),
                "top_p": kwargs.get("top_p", settings.top_p)
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"零一万物 API调用失败: {e}")
            raise
    
    def validate_config(self) -> bool:
        """验证零一万物配置"""
        return bool(self.api_key and self.model)

class ModelAdapterFactory:
    """模型适配器工厂类"""
    
    _adapters = {
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
        "deepseek": DeepSeekAdapter,
        "zhipu": ZhipuAdapter,
        "baichuan": BaichuanAdapter,
        "qwen": QwenAdapter,
        "moonshot": MoonshotAdapter,
        "yi": YiAdapter
    }
    
    @classmethod
    def create_adapter(cls, provider: str = None) -> BaseModelAdapter:
        """创建模型适配器"""
        if provider is None:
            provider = settings.model_provider
        
        if provider not in cls._adapters:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        config = get_current_model_config()
        adapter_class = cls._adapters[provider]
        adapter = adapter_class(config)
        
        if not adapter.validate_config():
            raise ValueError(f"{provider} 配置无效")
        
        return adapter
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持的模型提供商列表"""
        return list(cls._adapters.keys())

# 全局模型适配器实例
_model_adapter: Optional[BaseModelAdapter] = None

def get_model_adapter() -> BaseModelAdapter:
    """获取模型适配器实例"""
    global _model_adapter
    if _model_adapter is None:
        _model_adapter = ModelAdapterFactory.create_adapter()
    return _model_adapter

def reset_model_adapter():
    """重置模型适配器实例"""
    global _model_adapter
    _model_adapter = None