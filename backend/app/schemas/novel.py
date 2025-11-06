from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

# NovelStatus removed - using string status now


class NovelBase(BaseModel):
    title: str = Field(..., max_length=200)
    initial_prompt: Optional[str] = None
    status: Optional[str] = "draft"
    # 兼容旧版字段（仅用于请求与响应层，不写入 Novel 表）
    author: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None


class NovelCreate(NovelBase):
    # 预留可选 user_id（安全起见服务端忽略外部传入，仅从登录用户获取）
    user_id: Optional[int] = None


class NovelUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    initial_prompt: Optional[str] = None
    status: Optional[str] = None


class NovelResponse(NovelBase):
    id: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
