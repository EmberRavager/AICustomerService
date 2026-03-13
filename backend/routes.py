#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由模块
定义所有的API接口
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any, AsyncGenerator
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger
import traceback
import uuid
import json

from config import get_settings
from services.chat_service import ChatService
from services.memory_service import MemoryService
from services.knowledge_service import KnowledgeService
from services.policy_service import PolicyService
from services.tenant_service import TenantService
from auth import create_access_token, require_admin
from models.chat_models import (
    ChatRequest, ChatResponse, ChatHistory, ConversationSummary,
    ChatSettings, KnowledgeBase, MessageType
)

# 创建路由器
health_router = APIRouter(prefix="/api", tags=["health"])
chat_router = APIRouter(prefix="/api/chat", tags=["chat"])
knowledge_router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])
order_router = APIRouter(prefix="/api/orders", tags=["orders"])
policy_router = APIRouter(prefix="/api/policy", tags=["policy"])
tenant_router = APIRouter(prefix="/api/tenants", tags=["tenants"])
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

# 依赖注入：获取服务实例
def get_chat_service() -> ChatService:
    return ChatService()

def get_memory_service() -> MemoryService:
    return MemoryService()

def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()

def get_policy_service() -> PolicyService:
    return PolicyService()

def get_tenant_service() -> TenantService:
    return TenantService()

def get_tenant_id(request: Request, tenant_service: TenantService = Depends(get_tenant_service)) -> Optional[str]:
    api_key = request.headers.get("X-Tenant-Key")
    if not api_key:
        return None
    tenant_id = tenant_service.get_tenant_by_key(api_key)
    if not tenant_id:
        raise HTTPException(status_code=401, detail="无效的租户Key")
    return tenant_id

class OrderStatusCallback(BaseModel):
    """订单状态回调"""
    session_id: Optional[str] = Field(None, description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    order_id: Optional[str] = Field(None, description="订单ID")
    item_id: Optional[str] = Field(None, description="商品ID")
    status: Optional[str] = Field(None, description="订单状态")
    raw_status: Optional[str] = Field(None, description="原始状态文案")
    reply_text: Optional[str] = Field(None, description="自定义自动发货回复")

class TenantCreateRequest(BaseModel):
    """创建租户请求"""
    name: str = Field(..., description="租户名称")
    api_key: Optional[str] = Field(None, description="租户API Key，不传则自动生成")
    model_provider: Optional[str] = Field(None, description="模型提供商")
    model_config: Optional[Dict[str, Any]] = Field(None, description="模型配置")

class TenantUpdateRequest(BaseModel):
    """更新租户配置请求"""
    api_key: Optional[str] = Field(None, description="租户API Key")
    model_provider: Optional[str] = Field(None, description="模型提供商")
    model_config: Optional[Dict[str, Any]] = Field(None, description="模型配置")

class TenantResetKeyRequest(BaseModel):
    """重置租户Key请求"""
    tenant_id: str = Field(..., description="租户ID")

class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str = Field(..., description="管理员账号")
    password: str = Field(..., description="管理员密码")

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
    chat_service: ChatService = Depends(get_chat_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    发送聊天消息并获取AI回复
    """
    try:
        logger.info(f"收到聊天请求: session_id={request.session_id}, user_id={request.user_id}")
        
        # 处理聊天消息
        response = await chat_service.chat(request, tenant_id=tenant_id)
        
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
    chat_service: ChatService = Depends(get_chat_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    发送聊天消息并获取AI流式回复
    """
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            logger.info(f"收到流式聊天请求: session_id={request.session_id}, user_id={request.user_id}")
            
            # 处理流式聊天消息
            async for chunk in chat_service.chat_stream(request, tenant_id=tenant_id):
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
        media_type="text/event-stream",
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
    chat_service: ChatService = Depends(get_chat_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    获取指定会话的聊天历史记录
    """
    try:
        logger.info(f"获取聊天历史: session_id={session_id}, limit={limit}, offset={offset}")
        
        history = await chat_service.get_chat_history(session_id, limit or 50, offset or 0, tenant_id=tenant_id)
        
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
    chat_service: ChatService = Depends(get_chat_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    清除指定会话的聊天历史记录
    """
    try:
        logger.info(f"清除聊天历史: session_id={session_id}")
        
        await chat_service.clear_chat_history(session_id, tenant_id=tenant_id)
        
        return create_response(message="聊天历史已成功清除")
        
    except Exception as e:
        logger.error(f"清除聊天历史失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="清除聊天历史失败")

@chat_router.get("/sessions", response_model=Dict[str, Any])
async def get_chat_sessions(
    user_id: Optional[str] = Query(None, description="用户ID"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="返回会话数量限制"),
    offset: Optional[int] = Query(0, ge=0, description="偏移量"),
    memory_service: MemoryService = Depends(get_memory_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    获取用户的聊天会话列表
    """
    try:
        logger.info(f"获取聊天会话: user_id={user_id}, limit={limit}, offset={offset}")
        
        tenant_memory_service = MemoryService(tenant_id)
        sessions = await tenant_memory_service.get_user_sessions(user_id, limit or 20, offset or 0)
        
        return create_response(
            data=sessions,
            message=f"成功获取 {len(sessions)} 个会话"
        )
        
    except Exception as e:
        logger.error(f"获取聊天会话失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取聊天会话失败")

@chat_router.get("/sessions/{session_id}/meta", response_model=Dict[str, Any])
async def get_chat_session_meta(
    session_id: str,
    memory_service: MemoryService = Depends(get_memory_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    获取会话元信息
    """
    try:
        tenant_memory_service = MemoryService(tenant_id)
        meta = await tenant_memory_service.get_session_meta(session_id)
        return create_response(data=meta, message="获取会话信息成功")
    except Exception as e:
        logger.error(f"获取会话信息失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取会话信息失败")

@chat_router.post("/sessions/{session_id}/manual", response_model=Dict[str, Any])
async def set_manual_mode(
    session_id: str,
    enabled: bool = Query(..., description="是否开启人工接管"),
    memory_service: MemoryService = Depends(get_memory_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    设置人工接管模式
    """
    try:
        tenant_memory_service = MemoryService(tenant_id)
        meta = await tenant_memory_service.set_manual_mode(session_id, enabled)
        return create_response(data=meta, message="人工接管设置成功")
    except Exception as e:
        logger.error(f"设置人工接管失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="设置人工接管失败")

@chat_router.post("/sessions", response_model=Dict[str, Any])
async def create_chat_session(
    title: Optional[str] = None,
    user_id: Optional[str] = None,
    memory_service: MemoryService = Depends(get_memory_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    创建新的聊天会话
    """
    try:
        logger.info(f"创建新会话: title={title}, user_id={user_id}")
        
        tenant_memory_service = MemoryService(tenant_id)
        session = await tenant_memory_service.create_session(title, user_id)
        
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
    memory_service: MemoryService = Depends(get_memory_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    删除指定的聊天会话
    """
    try:
        logger.info(f"删除会话: session_id={session_id}")
        
        tenant_memory_service = MemoryService(tenant_id)
        await tenant_memory_service.delete_session(session_id)
        
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
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    搜索知识库内容
    """
    try:
        logger.info(f"搜索知识库: query={query}, limit={limit}, type={search_type}")
        
        tenant_knowledge_service = KnowledgeService(tenant_id)
        results = await tenant_knowledge_service.search_knowledge(
            query=query,
            limit=limit or 10,
            search_type=search_type or "hybrid"
        )
        
        return create_response(
            data=results,
            message=f"搜索完成，找到 {len(results)} 条相关内容"
        )
        
    except Exception as e:
        logger.error(f"搜索知识库失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="搜索知识库失败")

@knowledge_router.get("/items/{item_id}", response_model=Dict[str, Any])
async def get_item_info(
    item_id: str,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    获取闲鱼商品信息
    """
    try:
        tenant_knowledge_service = KnowledgeService(tenant_id)
        item_context = await tenant_knowledge_service.get_item_context(item_id)
        if not item_context:
            raise HTTPException(status_code=404, detail="未找到商品信息")

        return create_response(
            data=item_context,
            message="获取商品信息成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取商品信息失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取商品信息失败")

@order_router.post("/callback", response_model=Dict[str, Any])
async def order_status_callback(
    payload: OrderStatusCallback,
    memory_service: MemoryService = Depends(get_memory_service),
    policy_service: PolicyService = Depends(get_policy_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    订单状态回调（用于自动发货文本）
    """
    tenant_policy_service = PolicyService(tenant_id)
    tenant_memory_service = MemoryService(tenant_id)
    policy = tenant_policy_service.get_policy()
    auto_ship_policy = policy.get("auto_ship", {})
    if not auto_ship_policy.get("enabled", True):
        return create_response(
            data={"action": "ignored", "reason": "auto_ship_disabled"},
            message="自动发货已关闭"
        )

    status_text = payload.status or ""
    raw_status_text = payload.raw_status or ""
    paid_signals = set(auto_ship_policy.get("trigger_status", []))
    is_paid = status_text in paid_signals or any(signal in raw_status_text for signal in paid_signals)

    if not is_paid:
        return create_response(
            data={"action": "no_action", "status": status_text or raw_status_text},
            message="订单状态未触发自动发货"
        )

    reply_text = payload.reply_text or auto_ship_policy.get("reply_text")

    if payload.session_id:
        history_item = ChatHistory(
            id=str(uuid.uuid4()),
            session_id=payload.session_id,
            message_type=MessageType.ASSISTANT,
            content=reply_text,
            timestamp=datetime.now(),
            user_id=payload.user_id,
            metadata={
                "order_id": payload.order_id,
                "item_id": payload.item_id,
                "status": payload.status or payload.raw_status,
                "source": "order_callback"
            }
        )
        await tenant_memory_service.save_chat_history(history_item)

    return create_response(
        data={
            "action": "auto_ship",
            "reply": reply_text,
            "order_id": payload.order_id,
            "item_id": payload.item_id,
            "status": payload.status or payload.raw_status
        },
        message="已生成自动发货回复"
    )

@knowledge_router.post("/", response_model=Dict[str, Any])
async def add_knowledge(
    knowledge: KnowledgeBase,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    添加知识库内容
    """
    try:
        logger.info(f"添加知识库内容: title={knowledge.title}")
        
        tenant_knowledge_service = KnowledgeService(tenant_id)
        result = await tenant_knowledge_service.add_knowledge(knowledge)
        
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
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    更新知识库内容
    """
    try:
        logger.info(f"更新知识库内容: id={knowledge_id}, title={knowledge.title}")
        
        tenant_knowledge_service = KnowledgeService(tenant_id)
        result = await tenant_knowledge_service.update_knowledge(knowledge_id, knowledge)
        
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
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    删除知识库内容
    """
    try:
        logger.info(f"删除知识库内容: id={knowledge_id}")
        
        tenant_knowledge_service = KnowledgeService(tenant_id)
        await tenant_knowledge_service.delete_knowledge(knowledge_id)
        
        return create_response(message="知识库内容删除成功")
        
    except Exception as e:
        logger.error(f"删除知识库内容失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="删除知识库内容失败")

@knowledge_router.get("/list", response_model=Dict[str, Any])
async def list_knowledge(
    category: Optional[str] = Query(None, description="知识分类"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: Optional[int] = Query(0, ge=0, description="偏移量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    获取知识库列表
    """
    try:
        logger.info(f"获取知识库列表: category={category}, limit={limit}, offset={offset}")
        
        tenant_knowledge_service = KnowledgeService(tenant_id)
        knowledge_list = await tenant_knowledge_service.list_knowledge(
            category=category,
            limit=limit or 20,
            offset=offset or 0
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
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    获取知识库分类列表
    """
    try:
        logger.info("获取知识库分类列表")
        
        tenant_knowledge_service = KnowledgeService(tenant_id)
        categories = await tenant_knowledge_service.get_categories()
        
        return create_response(
            data=categories,
            message="获取分类列表成功"
        )
        
    except Exception as e:
        logger.error(f"获取知识库分类失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取知识库分类失败")

@policy_router.get("", response_model=Dict[str, Any])
async def get_policy(
    policy_service: PolicyService = Depends(get_policy_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """获取策略配置"""
    try:
        tenant_policy_service = PolicyService(tenant_id)
        policy = tenant_policy_service.get_policy()
        return create_response(data=policy, message="获取策略成功")
    except Exception as e:
        logger.error(f"获取策略失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取策略失败")

@policy_router.put("", response_model=Dict[str, Any])
async def update_policy(
    updates: Dict[str, Any],
    policy_service: PolicyService = Depends(get_policy_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """更新策略配置"""
    try:
        tenant_policy_service = PolicyService(tenant_id)
        policy = tenant_policy_service.update_policy(updates)
        return create_response(data=policy, message="更新策略成功")
    except Exception as e:
        logger.error(f"更新策略失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="更新策略失败")

@admin_router.post("/login", response_model=Dict[str, Any])
async def admin_login(payload: AdminLoginRequest):
    """管理员登录"""
    try:
        settings = get_settings()
        if payload.username != settings.admin_username or payload.password != settings.admin_password:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        token = create_access_token(payload.username)
        return create_response(data={"access_token": token}, message="登录成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员登录失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="登录失败")

@admin_router.get("/me", response_model=Dict[str, Any])
async def admin_me(username: str = Depends(require_admin)):
    """获取管理员信息"""
    return create_response(data={"username": username}, message="获取成功")

@tenant_router.post("", response_model=Dict[str, Any], dependencies=[Depends(require_admin)])
async def create_tenant(
    payload: TenantCreateRequest,
    tenant_service: TenantService = Depends(get_tenant_service)
):
    """创建租户"""
    try:
        tenant = tenant_service.create_tenant(payload.name, payload.api_key)
        updates = {}
        if payload.model_provider:
            updates["model_provider"] = payload.model_provider
        if payload.model_config:
            updates["model_config"] = payload.model_config
        if updates:
            tenant_service.update_tenant_config(tenant["tenant_id"], updates)

        return create_response(data=tenant, message="租户创建成功")
    except Exception as e:
        logger.error(f"创建租户失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="创建租户失败")

@tenant_router.get("/{tenant_id}", response_model=Dict[str, Any], dependencies=[Depends(require_admin)])
async def get_tenant_config(
    tenant_id: str,
    tenant_service: TenantService = Depends(get_tenant_service)
):
    """获取租户配置"""
    try:
        config = tenant_service.get_tenant_config(tenant_id)
        return create_response(data=config, message="获取租户配置成功")
    except Exception as e:
        logger.error(f"获取租户配置失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取租户配置失败")

@tenant_router.put("/{tenant_id}", response_model=Dict[str, Any], dependencies=[Depends(require_admin)])
async def update_tenant_config(
    tenant_id: str,
    payload: TenantUpdateRequest,
    tenant_service: TenantService = Depends(get_tenant_service)
):
    """更新租户配置"""
    try:
        updates = {}
        if payload.api_key:
            tenant_service.update_api_key(tenant_id, payload.api_key)
        if payload.model_provider:
            updates["model_provider"] = payload.model_provider
        if payload.model_config:
            updates["model_config"] = payload.model_config
        config = tenant_service.update_tenant_config(tenant_id, updates)
        return create_response(data=config, message="更新租户配置成功")
    except Exception as e:
        logger.error(f"更新租户配置失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="更新租户配置失败")

@tenant_router.get("", response_model=Dict[str, Any], dependencies=[Depends(require_admin)])
async def list_tenants(
    tenant_service: TenantService = Depends(get_tenant_service)
):
    """获取租户列表"""
    try:
        data = tenant_service.list_tenants()
        return create_response(data=data, message="获取租户列表成功")
    except Exception as e:
        logger.error(f"获取租户列表失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取租户列表失败")

@tenant_router.post("/reset-key", response_model=Dict[str, Any], dependencies=[Depends(require_admin)])
async def reset_tenant_key(
    payload: TenantResetKeyRequest,
    tenant_service: TenantService = Depends(get_tenant_service)
):
    """重置租户Key"""
    try:
        data = tenant_service.reset_api_key(payload.tenant_id)
        return create_response(data=data, message="租户Key已重置")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"重置租户Key失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="重置租户Key失败")

@knowledge_router.post("/batch", response_model=Dict[str, Any])
async def batch_add_knowledge(
    knowledge_list: List[KnowledgeBase],
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: Optional[str] = Depends(get_tenant_id)
):
    """
    批量添加知识库内容
    """
    try:
        logger.info(f"批量添加知识库内容: {len(knowledge_list)} 条")
        
        tenant_knowledge_service = KnowledgeService(tenant_id)
        results = await tenant_knowledge_service.batch_add_knowledge(knowledge_list)
        
        return create_response(
            data=results,
            message=f"批量添加完成，成功添加 {len(results)} 条内容"
        )
        
    except Exception as e:
        logger.error(f"批量添加知识库内容失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="批量添加知识库内容失败")

# 导出所有路由器
__all__ = ["health_router", "chat_router", "knowledge_router", "order_router", "policy_router", "tenant_router", "admin_router"]
