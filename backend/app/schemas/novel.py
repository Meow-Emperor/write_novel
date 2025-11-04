"""
小说数据传输对象(DTO)模式
定义API请求和响应的数据结构
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..models.novel import NovelStatus


class NovelBase(BaseModel):
    """小说基础模式 - 包含小说的通用字段"""
    title: str = Field(..., max_length=200)  # 标题（必填，最大200字符）
    author: Optional[str] = Field(None, max_length=100)  # 作者（可选，最大100字符）
    genre: Optional[str] = Field(None, max_length=50)  # 类型（可选，最大50字符）
    description: Optional[str] = None  # 简介（可选）
    status: Optional[NovelStatus] = NovelStatus.DRAFT  # 状态（默认为草稿）


class NovelCreate(NovelBase):
    """小说创建模式 - 用于POST请求创建新小说"""
    pass


class NovelUpdate(BaseModel):
    """小说更新模式 - 用于PUT/PATCH请求更新小说，所有字段可选"""
    title: Optional[str] = Field(None, max_length=200)  # 标题
    author: Optional[str] = Field(None, max_length=100)  # 作者
    genre: Optional[str] = Field(None, max_length=50)  # 类型
    description: Optional[str] = None  # 简介
    status: Optional[NovelStatus] = None  # 状态


class NovelResponse(NovelBase):
    """小说响应模式 - 用于API返回小说数据，包含ID和时间戳"""
    id: UUID  # 唯一标识符
    created_at: datetime  # 创建时间
    updated_at: datetime  # 更新时间

    class Config:
        from_attributes = True  # 允许从ORM模型属性读取数据
