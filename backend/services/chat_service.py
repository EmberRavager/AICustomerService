#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天服务模块
基于LangChain实现的智能客服核心逻辑
"""

import uuid
import asyncio
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
from loguru import logger

from config import get_settings
from models.model_adapter import get_model_adapter, reset_model_adapter
from models.chat_models import (
    ChatRequest, ChatResponse, ChatHistory,
    MessageType, ChatSettings
)
from services.memory_service import MemoryService
from services.knowledge_service import KnowledgeService

class TokenCounterCallback:
    """Token计数回调处理器"""
    
    def __init__(self):
        self.token_count = 0
        self.model_name = ""
        self.input_tokens = 0
        self.output_tokens = 0
    
    def update_token_count(self, input_tokens: int = 0, output_tokens: int = 0, model_name: str = ""):
        """更新token计数"""
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.token_count = input_tokens + output_tokens
        self.model_name = model_name

class ChatService:
    """聊天服务类"""
    
    def __init__(self):
        """初始化聊天服务"""
        self.settings = get_settings()
        self.memory_service = MemoryService()
        self.knowledge_service = KnowledgeService()
        self.chat_settings = ChatSettings()
        
        # 初始化模型适配器
        self._init_model_adapter()
        
        logger.info("聊天服务初始化完成")
    
    def _init_model_adapter(self):
        """初始化模型适配器"""
        try:
            # 重置并获取新的模型适配器
            reset_model_adapter()
            self.model_adapter = get_model_adapter()
            
            logger.info(f"模型适配器初始化成功，使用提供商: {self.settings.model_provider}")
            
        except Exception as e:
            logger.error(f"模型适配器初始化失败: {str(e)}")
            raise
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        try:
            # 生成会话ID（如果没有提供）
            session_id = request.session_id or str(uuid.uuid4())
            
            # 保存用户消息到历史记录
            await self._save_message_to_history(
                session_id=session_id,
                message_type=MessageType.USER,
                content=request.message,
                user_id=request.user_id
            )
            
            # 获取对话历史
            conversation_history = await self.memory_service.get_conversation_memory(session_id)
            
            # 构建消息列表
            messages = await self._build_messages(
                user_message=request.message,
                conversation_history=conversation_history,
                context=request.context
            )
            
            # 创建token计数器
            token_counter = TokenCounterCallback()
            
            # 调用LLM生成回复
            response_message = await self._generate_response(
                messages=messages,
                callback=token_counter
            )
            
            # 保存AI回复到历史记录
            await self._save_message_to_history(
                session_id=session_id,
                message_type=MessageType.ASSISTANT,
                content=response_message,
                user_id=request.user_id
            )
            
            # 更新对话记忆
            await self.memory_service.update_conversation_memory(
                session_id=session_id,
                user_message=request.message,
                ai_message=response_message
            )
            
            # 构建响应
            response = ChatResponse(
                message=response_message,
                session_id=session_id,
                timestamp=datetime.now(),
                tokens_used=token_counter.token_count,
                model_used=token_counter.model_name or self.settings.default_model,
                confidence=0.9  # 可以根据实际情况调整
            )
            
            return response
            
        except Exception as e:
            logger.error(f"聊天处理失败: {str(e)}")
            raise
    
    async def _build_messages(self, user_message: str, conversation_history: List[Dict], context: Optional[Dict] = None) -> List[Dict[str, str]]:
        """构建消息列表"""
        messages = []
        
        # 添加系统消息
        system_prompt = self._build_system_prompt(context)
        messages.append({"role": "system", "content": system_prompt})
        
        # 添加对话历史
        for history_item in conversation_history[-10:]:  # 只保留最近10轮对话
            if history_item['type'] == 'user':
                messages.append({"role": "user", "content": history_item['content']})
            elif history_item['type'] == 'assistant':
                messages.append({"role": "assistant", "content": history_item['content']})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _build_system_prompt(self, context: Optional[Dict] = None) -> str:
        """构建系统提示词"""
        base_prompt = self.settings.system_prompt
        
        # 根据上下文信息调整提示词
        if context:
            if context.get('source') == 'product':
                base_prompt += "\n\n请特别关注产品相关的咨询，提供详细和准确的产品信息。"
            elif context.get('source') == 'support':
                base_prompt += "\n\n请专注于技术支持和问题解决，提供清晰的解决方案。"
        
        # 添加当前时间信息
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_prompt += f"\n\n当前时间: {current_time}"
        
        return base_prompt
    
    async def _generate_response(self, messages: List[Dict[str, str]], callback: TokenCounterCallback) -> str:
        """生成AI回复"""
        try:
            # 异步调用模型适配器
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model_adapter.chat_completion(
                    messages=messages,
                    temperature=self.settings.temperature,
                    max_tokens=self.settings.max_tokens,
                    top_p=self.settings.top_p,
                    frequency_penalty=self.settings.frequency_penalty,
                    presence_penalty=self.settings.presence_penalty
                )
            )
            
            # 更新token计数（简化版本，实际token计数需要根据具体模型API返回值）
            callback.update_token_count(
                input_tokens=self._estimate_tokens(messages),
                output_tokens=self._estimate_tokens([{"role": "assistant", "content": response}]),
                model_name=self.model_adapter.model
            )
            
            return response
            
        except Exception as e:
            logger.error(f"模型API调用失败: {str(e)}")
            # 返回默认回复
            return "抱歉，我现在无法处理您的请求，请稍后再试。"
    
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式聊天处理
        """
        try:
            # 验证请求
            if not request.message or not request.message.strip():
                raise ValueError("消息内容不能为空")
            
            # 获取会话历史
            conversation_history = await self.memory_service.get_chat_history(
                session_id=request.session_id,
                limit=self.chat_settings.max_history_length
            )
            
            # 搜索相关知识
            context = None
            if self.chat_settings.enable_knowledge_base:
                try:
                    knowledge_results = await self.knowledge_service.search(
                        query=request.message,
                        limit=3,
                        search_type="hybrid"
                    )
                    if knowledge_results:
                        context = {
                            "knowledge": knowledge_results,
                            "search_query": request.message
                        }
                except Exception as e:
                    logger.warning(f"知识库搜索失败: {e}")
            
            # 构建消息列表
            messages = await self._build_messages(
                user_message=request.message,
                conversation_history=conversation_history,
                context=context
            )
            
            # 保存用户消息到历史记录
            await self._save_message_to_history(
                session_id=request.session_id,
                message_type=MessageType.USER,
                content=request.message,
                user_id=request.user_id
            )
            
            # 流式生成AI回复
            full_response = ""
            async for chunk in self._generate_response_stream(messages):
                full_response += chunk
                
                # 发送流式数据块
                yield {
                    "type": "content",
                    "content": chunk,
                    "session_id": request.session_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 保存AI回复到历史记录
            await self._save_message_to_history(
                session_id=request.session_id,
                message_type=MessageType.ASSISTANT,
                content=full_response,
                user_id=request.user_id
            )
            
            # 发送完成信号
            yield {
                "type": "done",
                "session_id": request.session_id,
                "full_content": full_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"流式聊天处理失败: {str(e)}")
            yield {
                "type": "error",
                "error": str(e),
                "session_id": request.session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_response_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        流式生成AI回复
        """
        try:
            # 模拟流式响应（实际实现需要根据具体模型API）
            response = await self._generate_response(messages, TokenCounterCallback())
            
            # 将完整响应分块发送（模拟流式效果）
            words = response.split()
            for i, word in enumerate(words):
                if i == 0:
                    yield word
                else:
                    yield " " + word
                
                # 添加延迟模拟真实的流式效果
                await asyncio.sleep(0.05)
                
        except Exception as e:
            logger.error(f"流式响应生成失败: {str(e)}")
            yield "抱歉，我现在无法处理您的请求，请稍后再试。"
    
    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """估算token数量（简化版本）"""
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        # 粗略估算：中文约1.5字符/token，英文约4字符/token
        return int(total_chars / 2.5)
    
    async def _save_message_to_history(
        self, 
        session_id: str, 
        message_type: MessageType, 
        content: str, 
        user_id: Optional[str] = None
    ):
        """保存消息到历史记录"""
        try:
            history_item = ChatHistory(
                id=str(uuid.uuid4()),
                session_id=session_id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now(),
                user_id=user_id
            )
            
            await self.memory_service.save_chat_history(history_item)
            
        except Exception as e:
            logger.error(f"保存聊天历史失败: {str(e)}")
    
    async def get_chat_history(self, session_id: str, limit: int = 50, offset: int = 0) -> List[ChatHistory]:
        """获取聊天历史
        
        Args:
            session_id: 会话ID
            limit: 返回的消息数量限制
            offset: 偏移量，用于分页
            
        Returns:
            聊天历史列表
        """
        try:
            # 获取完整的聊天历史
            full_history = await self.memory_service.get_chat_history(session_id, limit + offset)
            # 应用偏移量和限制
            return full_history[offset:offset + limit]
        except Exception as e:
            logger.error(f"获取聊天历史失败: {str(e)}")
            return []
    
    async def clear_chat_history(self, session_id: str):
        """清除聊天历史"""
        try:
            await self.memory_service.clear_chat_history(session_id)
            logger.info(f"聊天历史已清除: {session_id}")
        except Exception as e:
            logger.error(f"清除聊天历史失败: {str(e)}")
            raise
    
    async def get_chat_sessions(self) -> List[str]:
        """获取所有聊天会话"""
        try:
            return await self.memory_service.get_all_sessions()
        except Exception as e:
            logger.error(f"获取聊天会话失败: {str(e)}")
            return []
    
    def update_chat_settings(self, settings: ChatSettings):
        """更新聊天设置"""
        try:
            self.chat_settings = settings
            
            # 重新初始化LLM
            self.llm = ChatOpenAI(
                model_name=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                openai_api_key=self.settings.openai_api_key,
                openai_api_base=self.settings.openai_api_base
            )
            
            logger.info(f"聊天设置已更新: {settings.model}")
            
        except Exception as e:
            logger.error(f"更新聊天设置失败: {str(e)}")
            raise