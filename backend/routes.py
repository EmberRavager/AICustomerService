#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由模块
定义所有的API接口
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
from loguru import logger
import traceback
import json

from config import get_settings
from services.chat_service import ChatService
from services.memory_service import MemoryService
from services.knowledge_service import KnowledgeService
from models.chat_models import (
    ChatRequest, ChatResponse, ChatHistory, ConversationSummary,
    ChatSettings, KnowledgeBase
)

# 创建路由器
health_router = APIRouter(prefix="/api", tags=["health"])
chat_router = APIRouter(prefix="/api/chat", tags=["chat"])
knowledge_router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

# 依赖注入：获取服务实例
def get_chat_service() -> ChatService:
    return ChatService()

def get_memory_service() -> MemoryService:
    return MemoryService()

def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()

# 统一响应格式
def create_response(data: Any = None, message: str = "操作成功", success: bool = True, code: int = 200) -> Dict[str, Any]:
    """
    创建统一的API响应格式
    """
    return {
        "success": success,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

# 健康检查相关接口
@health_router.get("/health")
async def health_check():
    """
    系统健康检查接口
    """
    try:
        # 检查各个服务的状态
        chat_service = get_chat_service()
        memory_service = get_memory_service()
        knowledge_service = get_knowledge_service()
        
        # 简单的服务可用性检查
        health_data = {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": "运行中",
            "services": {
                "chat_service": "available",
                "memory_service": "available",
                "knowledge_service": "available",
                "ai_service": "available"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return create_response(data=health_data, message="系统运行正常")
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content=create_response(
                success=False,
                code=503,
                message=f"系统异常: {str(e)}"
            )
        )

# 聊天相关接口
@chat_router.post("/", response_model=Dict[str, Any])
async def send_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    发送聊天消息并获取AI回复
    """
    try:
        logger.info(f"收到聊天请求: session_id={request.session_id}, user_id={request.user_id}")
        
        # 处理聊天消息
        response = await chat_service.chat(request)
        
        logger.info(f"聊天处理完成: session_id={response.session_id}")
        return create_response(data=response.dict(), message="消息发送成功")
        
    except ValueError as e:
        logger.warning(f"请求参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理聊天消息失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")

@chat_router.post("/stream")
async def send_message_stream(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    发送聊天消息并获取AI流式回复
    """
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            logger.info(f"收到流式聊天请求: session_id={request.session_id}, user_id={request.user_id}")
            
            # 处理流式聊天消息
            async for chunk in chat_service.chat_stream(request):
                # 发送数据块，格式为 Server-Sent Events
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                
            # 发送结束标记
            yield "data: [DONE]\n\n"
            
            logger.info(f"流式聊天处理完成: session_id={request.session_id}")
            
        except ValueError as e:
            logger.warning(f"请求参数错误: {e}")
            error_data = {"error": str(e), "type": "validation_error"}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"处理流式聊天消息失败: {e}\n{traceback.format_exc()}")
            error_data = {"error": "服务器内部错误，请稍后重试", "type": "server_error"}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@chat_router.get("/history", response_model=Dict[str, Any])
async def get_chat_history(
    session_id: str = Query(..., description="会话ID"),
    limit: Optional[int] = Query(50, ge=1, le=200, description="返回记录数量限制"),
    offset: Optional[int] = Query(0, ge=0, description="偏移量"),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    获取指定会话的聊天历史记录
    """
    try:
        logger.info(f"获取聊天历史: session_id={session_id}, limit={limit}, offset={offset}")
        
        history = await chat_service.get_chat_history(session_id, limit, offset)
        
        return create_response(
            data=history,
            message=f"成功获取 {len(history)} 条历史记录"
        )
        
    except Exception as e:
        logger.error(f"获取聊天历史失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取聊天历史失败")

@chat_router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    清除指定会话的聊天历史记录
    """
    try:
        logger.info(f"清除聊天历史: session_id={session_id}")
        
        await chat_service.clear_chat_history(session_id)
        
        return create_response(message="聊天历史已成功清除")
        
    except Exception as e:
        logger.error(f"清除聊天历史失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="清除聊天历史失败")

@chat_router.get("/sessions", response_model=Dict[str, Any])
async def get_chat_sessions(
    user_id: Optional[str] = Query(None, description="用户ID"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="返回会话数量限制"),
    offset: Optional[int] = Query(0, ge=0, description="偏移量"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    获取用户的聊天会话列表
    """
    try:
        logger.info(f"获取聊天会话: user_id={user_id}, limit={limit}, offset={offset}")
        
        sessions = await memory_service.get_user_sessions(user_id, limit, offset)
        
        return create_response(
            data=sessions,
            message=f"成功获取 {len(sessions)} 个会话"
        )
        
    except Exception as e:
        logger.error(f"获取聊天会话失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取聊天会话失败")

@chat_router.post("/sessions", response_model=Dict[str, Any])
async def create_chat_session(
    title: Optional[str] = None,
    user_id: Optional[str] = None,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    创建新的聊天会话
    """
    try:
        logger.info(f"创建新会话: title={title}, user_id={user_id}")
        
        session = await memory_service.create_session(title, user_id)
        
        return create_response(
            data=session,
            message="会话创建成功"
        )
        
    except Exception as e:
        logger.error(f"创建会话失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="创建会话失败")

@chat_router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    删除指定的聊天会话
    """
    try:
        logger.info(f"删除会话: session_id={session_id}")
        
        await memory_service.delete_session(session_id)
        
        return create_response(message="会话删除成功")
        
    except Exception as e:
        logger.error(f"删除会话失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="删除会话失败")

@chat_router.get("/settings", response_model=Dict[str, Any])
async def get_chat_settings(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    获取聊天设置
    """
    try:
        settings_data = await chat_service.get_chat_settings()
        
        return create_response(
            data=settings_data,
            message="获取设置成功"
        )
        
    except Exception as e:
        logger.error(f"获取聊天设置失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取聊天设置失败")

@chat_router.put("/settings", response_model=Dict[str, Any])
async def update_chat_settings(
    settings_update: ChatSettings,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    更新聊天设置
    """
    try:
        logger.info(f"更新聊天设置: {settings_update.dict()}")
        
        updated_settings = await chat_service.update_chat_settings(settings_update)
        
        return create_response(
            data=updated_settings,
            message="设置更新成功"
        )
        
    except Exception as e:
        logger.error(f"更新聊天设置失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="更新聊天设置失败")

# 知识库相关接口
@knowledge_router.get("/", response_model=Dict[str, Any])
async def search_knowledge(
    query: str = Query(..., description="搜索关键词"),
    limit: Optional[int] = Query(10, ge=1, le=50, description="返回结果数量限制"),
    search_type: Optional[str] = Query("hybrid", description="搜索类型: vector, keyword, hybrid"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    搜索知识库内容
    """
    try:
        logger.info(f"搜索知识库: query={query}, limit={limit}, type={search_type}")
        
        results = await knowledge_service.search_knowledge(
            query=query,
            limit=limit,
            search_type=search_type
        )
        
        return create_response(
            data=results,
            message=f"搜索完成，找到 {len(results)} 条相关内容"
        )
        
    except Exception as e:
        logger.error(f"搜索知识库失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="搜索知识库失败")

@knowledge_router.post("/", response_model=Dict[str, Any])
async def add_knowledge(
    knowledge: KnowledgeBase,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    添加知识库内容
    """
    try:
        logger.info(f"添加知识库内容: title={knowledge.title}")
        
        result = await knowledge_service.add_knowledge(knowledge)
        
        return create_response(
            data=result,
            message="知识库内容添加成功"
        )
        
    except Exception as e:
        logger.error(f"添加知识库内容失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="添加知识库内容失败")

@knowledge_router.put("/{knowledge_id}", response_model=Dict[str, Any])
async def update_knowledge(
    knowledge_id: str,
    knowledge: KnowledgeBase,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    更新知识库内容
    """
    try:
        logger.info(f"更新知识库内容: id={knowledge_id}, title={knowledge.title}")
        
        result = await knowledge_service.update_knowledge(knowledge_id, knowledge)
        
        return create_response(
            data=result,
            message="知识库内容更新成功"
        )
        
    except Exception as e:
        logger.error(f"更新知识库内容失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="更新知识库内容失败")

@knowledge_router.delete("/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: str,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    删除知识库内容
    """
    try:
        logger.info(f"删除知识库内容: id={knowledge_id}")
        
        await knowledge_service.delete_knowledge(knowledge_id)
        
        return create_response(message="知识库内容删除成功")
        
    except Exception as e:
        logger.error(f"删除知识库内容失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="删除知识库内容失败")

@knowledge_router.get("/list", response_model=Dict[str, Any])
async def list_knowledge(
    category: Optional[str] = Query(None, description="知识分类"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: Optional[int] = Query(0, ge=0, description="偏移量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取知识库列表
    """
    try:
        logger.info(f"获取知识库列表: category={category}, limit={limit}, offset={offset}")
        
        knowledge_list = await knowledge_service.list_knowledge(
            category=category,
            limit=limit,
            offset=offset
        )
        
        return create_response(
            data=knowledge_list,
            message=f"成功获取 {len(knowledge_list)} 条知识库内容"
        )
        
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取知识库列表失败")

@knowledge_router.get("/categories", response_model=Dict[str, Any])
async def get_knowledge_categories(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取知识库分类列表
    """
    try:
        logger.info("获取知识库分类列表")
        
        categories = await knowledge_service.get_categories()
        
        return create_response(
            data=categories,
            message="获取分类列表成功"
        )
        
    except Exception as e:
        logger.error(f"获取知识库分类失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取知识库分类失败")

@knowledge_router.post("/batch", response_model=Dict[str, Any])
async def batch_add_knowledge(
    knowledge_list: List[KnowledgeBase],
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    批量添加知识库内容
    """
    try:
        logger.info(f"批量添加知识库内容: {len(knowledge_list)} 条")
        
        results = await knowledge_service.batch_add_knowledge(knowledge_list)
        
        return create_response(
            data=results,
            message=f"批量添加完成，成功添加 {len(results)} 条内容"
        )
        
    except Exception as e:
        logger.error(f"批量添加知识库内容失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="批量添加知识库内容失败")

# 导出所有路由器
__all__ = ["health_router", "chat_router", "knowledge_router"]