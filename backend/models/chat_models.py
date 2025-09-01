#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天相关数据模型
定义聊天请求、响应和历史记录的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    """消息类型枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息内容", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="会话ID，用于维持对话上下文")
    user_id: Optional[str] = Field(None, description="用户ID")
    context: Optional[Dict[str, Any]] = Field(None, description="额外的上下文信息")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "你好，我想咨询一下产品信息",
                "session_id": "session_123",
                "user_id": "user_456",
                "context": {"source": "web", "page": "product"}
            }
        }

class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str = Field(..., description="AI助手回复内容")
    session_id: str = Field(..., description="会话ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    tokens_used: Optional[int] = Field(None, description="使用的token数量")
    model_used: Optional[str] = Field(None, description="使用的模型名称")
    confidence: Optional[float] = Field(None, description="回复置信度", ge=0.0, le=1.0)
    
    class Config:
        schema_extra = {
            "example": {
                "message": "您好！我很乐意为您介绍我们的产品信息。请问您想了解哪方面的内容呢？",
                "session_id": "session_123",
                "timestamp": "2024-01-01T12:00:00",
                "tokens_used": 50,
                "model_used": "gpt-3.5-turbo",
                "confidence": 0.95
            }
        }

class ChatHistory(BaseModel):
    """聊天历史记录模型"""
    id: Optional[str] = Field(None, description="记录ID")
    session_id: str = Field(..., description="会话ID")
    message_type: MessageType = Field(..., description="消息类型")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    user_id: Optional[str] = Field(None, description="用户ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "msg_789",
                "session_id": "session_123",
                "message_type": "user",
                "content": "你好，我想咨询一下产品信息",
                "timestamp": "2024-01-01T12:00:00",
                "user_id": "user_456",
                "metadata": {"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"}
            }
        }

class ConversationSummary(BaseModel):
    """对话摘要模型"""
    session_id: str = Field(..., description="会话ID")
    summary: str = Field(..., description="对话摘要")
    key_points: List[str] = Field(default_factory=list, description="关键要点")
    sentiment: Optional[str] = Field(None, description="情感倾向")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
class KnowledgeBase(BaseModel):
    """知识库条目模型"""
    id: Optional[str] = Field(None, description="条目ID")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    category: Optional[str] = Field(None, description="分类")
    tags: List[str] = Field(default_factory=list, description="标签")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
class ChatSettings(BaseModel):
    """聊天设置模型"""
    model: str = Field(default="gpt-3.5-turbo", description="使用的模型")
    temperature: float = Field(default=0.7, description="温度参数", ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, description="最大token数", gt=0)
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    enable_memory: bool = Field(default=True, description="是否启用记忆功能")
    memory_window: int = Field(default=10, description="记忆窗口大小", gt=0)