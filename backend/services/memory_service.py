#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆服务模块
管理对话历史、上下文记忆和会话状态
"""

import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

from models.chat_models import ChatHistory, MessageType, ConversationSummary
from config import get_settings

class MemoryService:
    """记忆服务类"""
    
    def __init__(self):
        """初始化记忆服务"""
        self.settings = get_settings()
        self.data_dir = "./data/memory"
        self.sessions_file = os.path.join(self.data_dir, "sessions.json")
        self.conversations_dir = os.path.join(self.data_dir, "conversations")
        
        # 创建必要的目录
        self._ensure_directories()
        
        # 内存中的会话缓存
        self.session_cache: Dict[str, List[Dict]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
        logger.info("记忆服务初始化完成")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.conversations_dir, exist_ok=True)
            
            # 如果sessions.json不存在，创建空文件
            if not os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            logger.error(f"创建目录失败: {str(e)}")
            raise
    
    async def save_chat_history(self, history_item: ChatHistory):
        """保存聊天历史记录"""
        try:
            session_id = history_item.session_id
            
            # 更新内存缓存
            if session_id not in self.session_cache:
                self.session_cache[session_id] = []
            
            history_dict = {
                "id": history_item.id,
                "type": history_item.message_type.value,
                "content": history_item.content,
                "timestamp": history_item.timestamp.isoformat(),
                "user_id": history_item.user_id,
                "metadata": history_item.metadata or {}
            }
            
            self.session_cache[session_id].append(history_dict)
            self.cache_expiry[session_id] = datetime.now() + timedelta(hours=1)
            
            # 持久化到文件
            await self._persist_conversation(session_id)
            
            # 更新会话索引
            await self._update_session_index(session_id, history_item.user_id)
            
            logger.debug(f"聊天历史已保存: {session_id}")
            
        except Exception as e:
            logger.error(f"保存聊天历史失败: {str(e)}")
            raise
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[ChatHistory]:
        """获取聊天历史记录"""
        try:
            # 先检查内存缓存
            if session_id in self.session_cache and self._is_cache_valid(session_id):
                history_data = self.session_cache[session_id][-limit:]
            else:
                # 从文件加载
                history_data = await self._load_conversation(session_id)
                if history_data:
                    self.session_cache[session_id] = history_data
                    self.cache_expiry[session_id] = datetime.now() + timedelta(hours=1)
                    history_data = history_data[-limit:]
                else:
                    history_data = []
            
            # 转换为ChatHistory对象
            chat_history = []
            for item in history_data:
                try:
                    chat_history.append(ChatHistory(
                        id=item.get("id"),
                        session_id=session_id,
                        message_type=MessageType(item["type"]),
                        content=item["content"],
                        timestamp=datetime.fromisoformat(item["timestamp"]),
                        user_id=item.get("user_id"),
                        metadata=item.get("metadata", {})
                    ))
                except Exception as e:
                    logger.warning(f"解析历史记录项失败: {str(e)}")
                    continue
            
            return chat_history
            
        except Exception as e:
            logger.error(f"获取聊天历史失败: {str(e)}")
            return []
    
    async def get_conversation_memory(self, session_id: str, window_size: int = 10) -> List[Dict]:
        """获取对话记忆（用于LangChain）"""
        try:
            history = await self.get_chat_history(session_id, window_size * 2)
            
            # 转换为简化格式
            memory = []
            for item in history:
                memory.append({
                    "type": item.message_type.value,
                    "content": item.content,
                    "timestamp": item.timestamp.isoformat()
                })
            
            return memory[-window_size:] if memory else []
            
        except Exception as e:
            logger.error(f"获取对话记忆失败: {str(e)}")
            return []
    
    async def update_conversation_memory(self, session_id: str, user_message: str, ai_message: str):
        """更新对话记忆"""
        try:
            # 这个方法主要用于触发记忆更新逻辑
            # 实际的保存已经在save_chat_history中完成
            
            # 检查是否需要生成对话摘要
            if session_id in self.session_cache:
                conversation_length = len(self.session_cache[session_id])
                if conversation_length > 0 and conversation_length % 20 == 0:
                    await self._generate_conversation_summary(session_id)
            
            logger.debug(f"对话记忆已更新: {session_id}")
            
        except Exception as e:
            logger.error(f"更新对话记忆失败: {str(e)}")
    
    async def clear_chat_history(self, session_id: str):
        """清除聊天历史"""
        try:
            # 清除内存缓存
            if session_id in self.session_cache:
                del self.session_cache[session_id]
            if session_id in self.cache_expiry:
                del self.cache_expiry[session_id]
            
            # 删除文件
            conversation_file = os.path.join(self.conversations_dir, f"{session_id}.json")
            if os.path.exists(conversation_file):
                os.remove(conversation_file)
            
            # 更新会话索引
            await self._remove_from_session_index(session_id)
            
            logger.info(f"聊天历史已清除: {session_id}")
            
        except Exception as e:
            logger.error(f"清除聊天历史失败: {str(e)}")
            raise
    
    async def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                return list(sessions_data.keys())
            return []
            
        except Exception as e:
            logger.error(f"获取会话列表失败: {str(e)}")
            return []
    
    async def get_user_sessions(self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """获取用户会话列表
        
        Args:
            user_id: 用户ID，如果为None则获取所有会话
            limit: 返回的会话数量限制
            offset: 偏移量，用于分页
            
        Returns:
            会话列表，包含会话ID、标题、创建时间、最后更新时间等信息
        """
        try:
            sessions = []
            
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                
                # 转换为列表格式，添加会话信息
                for session_id, session_info in sessions_data.items():
                    # 如果指定了用户ID，则过滤
                    if user_id and session_info.get('user_id') != user_id:
                        continue
                    
                    session_item = {
                        'id': session_id,
                        'title': session_info.get('title', f'会话 {session_id[:8]}'),
                        'created_at': session_info.get('created_at', datetime.now().isoformat()),
                        'updated_at': session_info.get('updated_at', datetime.now().isoformat()),
                        'user_id': session_info.get('user_id'),
                        'message_count': session_info.get('message_count', 0)
                    }
                    sessions.append(session_item)
                
                # 按更新时间倒序排列
                sessions.sort(key=lambda x: x['updated_at'], reverse=True)
                
                # 应用分页
                start_idx = offset
                end_idx = offset + limit
                return sessions[start_idx:end_idx]
            
            return []
            
        except Exception as e:
            logger.error(f"获取用户会话列表失败: {str(e)}")
            raise
    
    def _is_cache_valid(self, session_id: str) -> bool:
        """检查缓存是否有效"""
        if session_id not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[session_id]
    
    async def _persist_conversation(self, session_id: str):
        """持久化对话到文件"""
        try:
            if session_id not in self.session_cache:
                return
            
            conversation_file = os.path.join(self.conversations_dir, f"{session_id}.json")
            with open(conversation_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.session_cache[session_id], 
                    f, 
                    ensure_ascii=False, 
                    indent=2
                )
                
        except Exception as e:
            logger.error(f"持久化对话失败: {str(e)}")
    
    async def _load_conversation(self, session_id: str) -> List[Dict]:
        """从文件加载对话"""
        try:
            conversation_file = os.path.join(self.conversations_dir, f"{session_id}.json")
            if os.path.exists(conversation_file):
                with open(conversation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
            
        except Exception as e:
            logger.error(f"加载对话失败: {str(e)}")
            return []
    
    async def _update_session_index(self, session_id: str, user_id: Optional[str] = None):
        """更新会话索引"""
        try:
            sessions_data = {}
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
            
            sessions_data[session_id] = {
                "user_id": user_id,
                "created_at": sessions_data.get(session_id, {}).get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
                "message_count": len(self.session_cache.get(session_id, []))
            }
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"更新会话索引失败: {str(e)}")
    
    async def _remove_from_session_index(self, session_id: str):
        """从会话索引中移除"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                
                if session_id in sessions_data:
                    del sessions_data[session_id]
                    
                    with open(self.sessions_file, 'w', encoding='utf-8') as f:
                        json.dump(sessions_data, f, ensure_ascii=False, indent=2)
                        
        except Exception as e:
            logger.error(f"从会话索引移除失败: {str(e)}")
    
    async def _generate_conversation_summary(self, session_id: str):
        """生成对话摘要"""
        try:
            # 这里可以集成LLM来生成对话摘要
            # 暂时实现简单的统计摘要
            if session_id in self.session_cache:
                conversation = self.session_cache[session_id]
                user_messages = [msg for msg in conversation if msg["type"] == "user"]
                ai_messages = [msg for msg in conversation if msg["type"] == "assistant"]
                
                summary = ConversationSummary(
                    session_id=session_id,
                    summary=f"对话包含{len(user_messages)}条用户消息和{len(ai_messages)}条AI回复",
                    key_points=["智能客服对话"],
                    sentiment="neutral",
                    created_at=datetime.now()
                )
                
                # 保存摘要（这里可以扩展为保存到数据库）
                logger.info(f"对话摘要已生成: {session_id}")
                
        except Exception as e:
            logger.error(f"生成对话摘要失败: {str(e)}")
    
    async def cleanup_expired_sessions(self, days: int = 30):
        """清理过期的会话"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                
                expired_sessions = []
                for session_id, session_info in sessions_data.items():
                    updated_at = datetime.fromisoformat(session_info.get("updated_at", ""))
                    if updated_at < cutoff_date:
                        expired_sessions.append(session_id)
                
                # 删除过期会话
                for session_id in expired_sessions:
                    await self.clear_chat_history(session_id)
                
                logger.info(f"已清理{len(expired_sessions)}个过期会话")
                
        except Exception as e:
            logger.error(f"清理过期会话失败: {str(e)}")