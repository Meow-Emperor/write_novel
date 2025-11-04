"""
AI小说写作平台 - 主应用入口
提供小说管理、角色管理、世界观设定、情节结构、章节管理和AI辅助写作等功能
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import ai, chapters, characters, novels, plots, worlds
from .core.config import settings
from .core.database import Base, engine

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用实例
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# 配置CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # 允许的源列表
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 注册各功能模块的路由
app.include_router(novels.router)  # 小说管理
app.include_router(characters.router)  # 角色管理
app.include_router(worlds.router)  # 世界观设定
app.include_router(plots.router)  # 情节结构
app.include_router(chapters.router)  # 章节管理
app.include_router(ai.router)  # AI辅助写作


@app.get("/")
async def root():
    """根路径 - 返回应用名称"""
    return {"message": settings.APP_NAME}


@app.get("/health")
async def health():
    """健康检查接口 - 用于监控服务状态"""
    return {"status": "healthy"}
