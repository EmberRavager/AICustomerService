#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能客服系统 - 主应用入口

这是FastAPI应用的主入口文件，负责：
1. 创建FastAPI应用实例
2. 配置中间件和CORS
3. 注册路由
4. 配置日志
5. 启动应用

Author: AI Assistant
Date: 2024
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import uvicorn
from datetime import datetime
import traceback

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import get_settings
from routes import health_router, chat_router, knowledge_router, order_router, policy_router, tenant_router, admin_router
from api.model_api import router as model_router

# 获取配置
settings = get_settings()

# 配置日志
logger.remove()  # 移除默认处理器
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="1 day",
    retention="30 days",
    compression="zip"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("🚀 智能客服系统启动中...")
    
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    # 初始化服务
    try:
        # 这里可以添加数据库连接、缓存初始化等
        logger.info("✅ 服务初始化完成")
    except Exception as e:
        logger.error(f"❌ 服务初始化失败: {e}")
        raise
    
    logger.info("🎉 智能客服系统启动成功！")
    
    yield
    
    # 关闭时执行
    logger.info("🛑 智能客服系统正在关闭...")
    # 这里可以添加清理逻辑
    logger.info("👋 智能客服系统已关闭")

# 创建FastAPI应用实例
app = FastAPI(
    title="智能客服系统 API",
    description="基于LangChain和FastAPI的智能客服系统，提供聊天、知识库管理等功能",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        [
            "http://localhost:3000",  # React开发服务器
            "http://127.0.0.1:3000",
            "http://localhost:1111",
            "http://127.0.0.1:1111",
            "http://localhost:8080",  # 可能的前端端口
            "http://127.0.0.1:8080",
        ] + settings.get_allowed_origins()
    ) if settings.debug else settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 配置受信任主机中间件（生产环境）
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.get_allowed_hosts()
    )

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    记录所有HTTP请求
    """
    start_time = datetime.now()
    
    # 记录请求信息
    logger.info(
        f"📥 {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = (datetime.now() - start_time).total_seconds()
        
        # 记录响应信息
        logger.info(
            f"📤 {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # 记录错误
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"❌ {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.3f}s\n{traceback.format_exc()}"
        )
        raise

# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理HTTP异常
    """
    logger.warning(
        f"HTTP异常: {request.method} {request.url.path} - "
        f"Status: {exc.status_code} - Detail: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理未捕获的异常
    """
    logger.error(
        f"未处理异常: {request.method} {request.url.path} - "
        f"Error: {str(exc)}\n{traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": 500,
            "message": "服务器内部错误" if not settings.debug else str(exc),
            "data": None,
            "timestamp": datetime.now().isoformat()
        }
    )

# 注册路由
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(knowledge_router)
app.include_router(order_router)
app.include_router(policy_router)
app.include_router(tenant_router)
app.include_router(admin_router)
app.include_router(model_router)

# 静态文件服务（如果需要）
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 根路径
@app.get("/")
async def root():
    """
    根路径，返回API信息
    """
    return {
        "message": "欢迎使用智能客服系统 API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "文档已禁用",
        "health": "/api/health",
        "timestamp": datetime.now().isoformat()
    }

# 开发服务器启动函数
def start_dev_server():
    """
    启动开发服务器
    """
    logger.info("🔧 启动开发服务器...")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    start_dev_server()
