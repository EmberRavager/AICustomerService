#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天服务模块
基于LangChain实现的智能客服核心逻辑
"""

import uuid
import asyncio
import json
import re
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
from loguru import logger

from config import get_settings
from models.model_adapter import get_model_adapter, reset_model_adapter, ModelAdapterFactory
from models.chat_models import (
    ChatRequest, ChatResponse, ChatHistory,
    MessageType, ChatSettings
)
from services.memory_service import MemoryService
from services.knowledge_service import KnowledgeService
from services.policy_service import PolicyService
from services.tenant_service import TenantService

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
        self.policy_service = PolicyService()
        self.tenant_service = TenantService()
        self.chat_settings = ChatSettings(
            model=self.settings.default_model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            system_prompt=self.settings.system_prompt,
            enable_memory=True,
            memory_window=10,
            enable_knowledge_base=True,
            max_history_length=50
        )
        
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

    def _get_model_adapter(self, tenant_id: Optional[str] = None):
        """获取租户模型适配器"""
        if not tenant_id:
            return self.model_adapter

        tenant_config = self.tenant_service.get_tenant_config(tenant_id)
        provider = tenant_config.get("model_provider") or self.settings.model_provider
        config_override = tenant_config.get("model_config")
        if config_override:
            return ModelAdapterFactory.create_adapter(provider=provider, config_override=config_override)

        return ModelAdapterFactory.create_adapter(provider=provider)
    
    async def chat(self, request: ChatRequest, tenant_id: Optional[str] = None) -> ChatResponse:
        """处理聊天请求"""
        try:
            session_id = request.session_id or str(uuid.uuid4())

            memory_service = MemoryService(tenant_id)
            knowledge_service = KnowledgeService(tenant_id)
            policy_service = PolicyService(tenant_id)
            model_adapter = self._get_model_adapter(tenant_id)

            await self._save_message_to_history(
                session_id=session_id,
                message_type=MessageType.USER,
                content=request.message,
                user_id=request.user_id,
                tenant_id=tenant_id
            )

            policy = policy_service.get_policy()
            manual_policy = policy.get("manual_takeover", {})
            if manual_policy.get("enabled", True):
                session_meta = await memory_service.get_session_meta(session_id)
                if session_meta.get("manual_mode") is True:
                    response_message = "当前会话已转人工处理，已记录您的消息，请稍候。"
                    await self._save_message_to_history(
                        session_id=session_id,
                        message_type=MessageType.ASSISTANT,
                        content=response_message,
                        user_id=request.user_id,
                        tenant_id=tenant_id
                    )
                    return ChatResponse(
                        message=response_message,
                        session_id=session_id,
                        timestamp=datetime.now(),
                        tokens_used=0,
                        model_used=self.settings.default_model,
                        confidence=1.0
                    )

            risk_policy = policy.get("risk_guard", {})
            if risk_policy.get("enabled", True):
                if self._contains_risk_keywords(request.message, risk_policy.get("blocked_keywords", [])):
                    response_message = risk_policy.get("reply_text") or "[安全提醒]请通过平台沟通，避免私下交易风险。"
                    await self._save_message_to_history(
                        session_id=session_id,
                        message_type=MessageType.ASSISTANT,
                        content=response_message,
                        user_id=request.user_id,
                        tenant_id=tenant_id
                    )
                    return ChatResponse(
                        message=response_message,
                        session_id=session_id,
                        timestamp=datetime.now(),
                        tokens_used=0,
                        model_used=self.settings.default_model,
                        confidence=1.0
                    )

            if self.chat_settings.enable_memory:
                conversation_history = await memory_service.get_conversation_memory(
                    session_id,
                    window_size=self.chat_settings.memory_window
                )
            else:
                conversation_history = []

            context = request.context or {}
            item_id = self._get_item_id(request)
            if item_id:
                item_context = await knowledge_service.get_item_context(item_id)
                if item_context:
                    context = {**context, "item_id": item_id, "item_info": item_context}

            intent_policy = policy.get("intent_routing", {})
            intent = self._detect_intent(request.message, intent_policy)
            context = {**context, "intent": intent}
            if intent == "price":
                bargain_count = await memory_service.increment_bargain_count(session_id)
                context = {**context, "bargain_count": bargain_count}

            messages = await self._build_messages(
                user_message=request.message,
                conversation_history=conversation_history,
                context=context
            )

            token_counter = TokenCounterCallback()
            response_message = await self._generate_response(
                messages=messages,
                callback=token_counter,
                model_adapter=model_adapter
            )

            await self._save_message_to_history(
                session_id=session_id,
                message_type=MessageType.ASSISTANT,
                content=response_message,
                user_id=request.user_id,
                tenant_id=tenant_id
            )

            await memory_service.update_conversation_memory(
                session_id=session_id,
                user_message=request.message,
                ai_message=response_message
            )

            return ChatResponse(
                message=response_message,
                session_id=session_id,
                timestamp=datetime.now(),
                tokens_used=token_counter.token_count,
                model_used=token_counter.model_name or model_adapter.model or self.settings.default_model,
                confidence=0.9
            )

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
        if self.chat_settings.enable_memory:
            memory_window = self.chat_settings.memory_window
            for history_item in conversation_history[-memory_window:]:
                if history_item["type"] == "user":
                    messages.append({"role": "user", "content": history_item["content"]})
                elif history_item["type"] == "assistant":
                    messages.append({"role": "assistant", "content": history_item["content"]})
        
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

            intent = context.get("intent")
            if intent == "price":
                bargain_count = context.get("bargain_count", 0)
                base_prompt += f"\n\n你是议价助手，当前议价轮次: {bargain_count}。请礼貌回应并给出合理让价策略。"
            elif intent == "tech":
                base_prompt += "\n\n你是技术咨询助手，请优先给出参数、规格与对比结论。"
            else:
                base_prompt += "\n\n你是二手平台客服助手，优先解释交易流程与平台规则。"
        
        # 注入商品信息
        if context and context.get("item_info"):
            item_info = context.get("item_info")
            base_prompt += "\n\n【商品信息】\n" + json.dumps(item_info, ensure_ascii=False)

        # 添加当前时间信息
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_prompt += f"\n\n当前时间: {current_time}"
        
        return base_prompt
    
    async def _generate_response(
        self,
        messages: List[Dict[str, str]],
        callback: TokenCounterCallback,
        model_adapter: Optional[Any] = None
    ) -> str:
        """生成AI回复"""
        try:
            adapter = model_adapter or self.model_adapter
            # 异步调用模型适配器
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: adapter.chat_completion(
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
                model_name=adapter.model or ""
            )
            
            return response
            
        except Exception as e:
            logger.error(f"模型API调用失败: {str(e)}")
            # 返回默认回复
            return "抱歉，我现在无法处理您的请求，请稍后再试。"
    
    async def chat_stream(self, request: ChatRequest, tenant_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式聊天处理
        """
        try:
            # 验证请求
            if not request.message or not request.message.strip():
                raise ValueError("消息内容不能为空")

            session_id = request.session_id or str(uuid.uuid4())

            memory_service = MemoryService(tenant_id)
            knowledge_service = KnowledgeService(tenant_id)
            policy_service = PolicyService(tenant_id)
            model_adapter = self._get_model_adapter(tenant_id)

            # 保存用户消息到历史记录
            await self._save_message_to_history(
                session_id=session_id,
                message_type=MessageType.USER,
                content=request.message,
                user_id=request.user_id,
                tenant_id=tenant_id
            )

            # 策略检查
            policy = policy_service.get_policy()
            manual_policy = policy.get("manual_takeover", {})
            if manual_policy.get("enabled", True):
                session_meta = await memory_service.get_session_meta(session_id)
                if session_meta.get("manual_mode") is True:
                    response_message = "当前会话已转人工处理，已记录您的消息，请稍候。"
                    await self._save_message_to_history(
                        session_id=session_id,
                        message_type=MessageType.ASSISTANT,
                        content=response_message,
                        user_id=request.user_id,
                        tenant_id=tenant_id
                    )
                    yield {"type": "content", "content": response_message, "session_id": session_id}
                    yield {"type": "done", "full_content": response_message, "session_id": session_id}
                    return

            risk_policy = policy.get("risk_guard", {})
            if risk_policy.get("enabled", True):
                if self._contains_risk_keywords(request.message, risk_policy.get("blocked_keywords", [])):
                    response_message = risk_policy.get("reply_text") or "[安全提醒]请通过平台沟通，避免私下交易风险。"
                    await self._save_message_to_history(
                        session_id=session_id,
                        message_type=MessageType.ASSISTANT,
                        content=response_message,
                        user_id=request.user_id,
                        tenant_id=tenant_id
                    )
                    yield {"type": "content", "content": response_message, "session_id": session_id}
                    yield {"type": "done", "full_content": response_message, "session_id": session_id}
                    return
            
            # 获取会话历史
            if self.chat_settings.enable_memory:
                conversation_history = await memory_service.get_conversation_memory(
                    session_id=session_id,
                    window_size=self.chat_settings.memory_window
                )
            else:
                conversation_history = []
            
            # 搜索相关知识/商品信息
            context = request.context or {}
            if self.chat_settings.enable_knowledge_base:
                item_id = self._get_item_id(request)
                if item_id:
                    item_context = await knowledge_service.get_item_context(item_id)
                    if item_context:
                        context = {**context, "item_id": item_id, "item_info": item_context}
                else:
                    try:
                        knowledge_results = await knowledge_service.search_knowledge(
                            query=request.message,
                            limit=3,
                            search_type="hybrid"
                        )
                        if knowledge_results:
                            context = {
                                **context,
                                "knowledge": knowledge_results,
                                "search_query": request.message
                            }
                    except Exception as e:
                        logger.warning(f"知识库搜索失败: {e}")

            # 意图路由
            intent_policy = policy.get("intent_routing", {})
            intent = self._detect_intent(request.message, intent_policy)
            context = {**context, "intent": intent}
            if intent == "price":
                bargain_count = await memory_service.increment_bargain_count(session_id)
                context = {**context, "bargain_count": bargain_count}
            
            # 构建消息列表
            messages = await self._build_messages(
                user_message=request.message,
                conversation_history=conversation_history,
                context=context
            )
            
            # 流式生成AI回复
            full_response = ""
            async for chunk in self._generate_response_stream(messages, model_adapter=model_adapter):
                full_response += chunk
                
                # 发送流式数据块
                yield {
                    "type": "content",
                    "content": chunk,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 保存AI回复到历史记录
            await self._save_message_to_history(
                session_id=session_id,
                message_type=MessageType.ASSISTANT,
                content=full_response,
                user_id=request.user_id,
                tenant_id=tenant_id
            )
            
            # 发送完成信号
            yield {
                "type": "done",
                "session_id": session_id,
                "full_content": full_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"流式聊天处理失败: {str(e)}")
            yield {
                "type": "error",
                "error": str(e),
                "session_id": request.session_id or "",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_response_stream(
        self,
        messages: List[Dict[str, str]],
        model_adapter: Optional[Any] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式生成AI回复
        """
        try:
            # 模拟流式响应（实际实现需要根据具体模型API）
            response = await self._generate_response(messages, TokenCounterCallback(), model_adapter=model_adapter)
            
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

    def _contains_risk_keywords(self, text: str, keywords: List[str]) -> bool:
        if not text or not keywords:
            return False
        return any(keyword in text for keyword in keywords)

    def _detect_intent(self, text: str, intent_policy: Dict[str, Any]) -> str:
        """基于关键词/正则的意图识别"""
        if not text:
            return "default"

        price_keywords = intent_policy.get("price_keywords", [])
        tech_keywords = intent_policy.get("tech_keywords", [])
        price_patterns = intent_policy.get("price_patterns", [])
        tech_patterns = intent_policy.get("tech_patterns", [])

        for keyword in tech_keywords:
            if keyword in text:
                return "tech"
        for pattern in tech_patterns:
            if re.search(pattern, text):
                return "tech"

        for keyword in price_keywords:
            if keyword in text:
                return "price"
        for pattern in price_patterns:
            if re.search(pattern, text):
                return "price"

        return "default"

    def _get_item_id(self, request: ChatRequest) -> Optional[str]:
        """从请求中提取商品ID"""
        if request.context and request.context.get("item_id"):
            return str(request.context.get("item_id"))
        return self._extract_item_id_from_text(request.message)

    def _extract_item_id_from_text(self, text: str) -> Optional[str]:
        """从文本中解析闲鱼商品ID"""
        if not text:
            return None
        patterns = [
            r"itemId=(\d+)",
            r"/item/(\d+)",
            r"itemId%3D(\d+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    async def _save_message_to_history(
        self, 
        session_id: str, 
        message_type: MessageType, 
        content: str, 
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ):
        """保存消息到历史记录"""
        try:
            memory_service = MemoryService(tenant_id)
            history_item = ChatHistory(
                id=str(uuid.uuid4()),
                session_id=session_id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now(),
                user_id=user_id
            )
            
            await memory_service.save_chat_history(history_item)
            
        except Exception as e:
            logger.error(f"保存聊天历史失败: {str(e)}")
    
    async def get_chat_history(self, session_id: str, limit: int = 50, offset: int = 0, tenant_id: Optional[str] = None) -> List[ChatHistory]:
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
            memory_service = MemoryService(tenant_id)
            full_history = await memory_service.get_chat_history(session_id, limit + offset)
            # 应用偏移量和限制
            return full_history[offset:offset + limit]
        except Exception as e:
            logger.error(f"获取聊天历史失败: {str(e)}")
            return []

    async def get_chat_settings(self) -> Dict[str, Any]:
        """获取聊天设置"""
        return self.chat_settings.dict()
    
    async def clear_chat_history(self, session_id: str, tenant_id: Optional[str] = None):
        """清除聊天历史"""
        try:
            memory_service = MemoryService(tenant_id)
            await memory_service.clear_chat_history(session_id)
            logger.info(f"聊天历史已清除: {session_id}")
        except Exception as e:
            logger.error(f"清除聊天历史失败: {str(e)}")
            raise
    
    async def get_chat_sessions(self, tenant_id: Optional[str] = None) -> List[str]:
        """获取所有聊天会话"""
        try:
            memory_service = MemoryService(tenant_id)
            return await memory_service.get_all_sessions()
        except Exception as e:
            logger.error(f"获取聊天会话失败: {str(e)}")
            return []
    
    async def update_chat_settings(self, settings: ChatSettings) -> Dict[str, Any]:
        """更新聊天设置"""
        try:
            self.chat_settings = settings

            self.settings.temperature = settings.temperature
            self.settings.max_tokens = settings.max_tokens
            if settings.system_prompt:
                self.settings.system_prompt = settings.system_prompt

            if settings.model:
                provider = self.settings.model_provider
                provider_model_key = f"{provider}_model"
                if hasattr(self.settings, provider_model_key):
                    setattr(self.settings, provider_model_key, settings.model)
                self.settings.default_model = settings.model

                reset_model_adapter()
                self.model_adapter = get_model_adapter()

            logger.info(f"聊天设置已更新: {settings.model}")
            return self.chat_settings.dict()
            
        except Exception as e:
            logger.error(f"更新聊天设置失败: {str(e)}")
            raise
