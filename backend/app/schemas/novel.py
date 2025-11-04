from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..models.novel import NovelStatus


class NovelBase(BaseModel):
    title: str = Field(..., max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[NovelStatus] = NovelStatus.DRAFT


class NovelCreate(NovelBase):
    pass


class NovelUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[NovelStatus] = None


class NovelResponse(NovelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
