#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能客服系统主入口文件
提供FastAPI服务和静态文件服务
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger

# 导入路由模块
from backend.routes import chat_router, health_router

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="智能客服系统",
    description="基于LangChain的智能客服系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

# 挂载静态文件服务
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("智能客服系统启动中...")
    logger.info("API文档地址: http://localhost:8000/docs")
    logger.info("前端界面地址: http://localhost:8000")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("智能客服系统正在关闭...")

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )