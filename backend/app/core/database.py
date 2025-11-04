"""
数据库配置模块
配置SQLAlchemy数据库引擎、会话和基础模型类
"""
from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# SQLite特定配置：禁用同线程检查（SQLite默认要求同一线程访问）
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# 创建数据库引擎
# pool_pre_ping: 每次从连接池获取连接时先ping一下，确保连接有效
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

# 创建会话工厂
# autocommit=False: 需要显式提交事务
# autoflush=False: 不自动刷新到数据库
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明式基类，所有模型类都继承自它
Base = declarative_base()


def get_db() -> Generator:
    """
    数据库会话依赖注入函数
    在FastAPI路由中使用Depends(get_db)获取数据库会话
    自动处理会话的创建和关闭
    """
    db = SessionLocal()
    try:
        yield db  # 返回会话给路由处理函数
    finally:
        db.close()  # 请求结束后自动关闭会话
