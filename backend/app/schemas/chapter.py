from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChapterBase(BaseModel):
    title: str = Field(..., max_length=200)
    chapter_number: int
    summary: Optional[str] = None
    content: Optional[str] = None
    word_count: int = Field(default=0)
    status: str = Field(default="DRAFT", max_length=50)
    notes: Optional[str] = None


class ChapterCreate(ChapterBase):
    novel_id: UUID


class ChapterUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    chapter_number: Optional[int] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    word_count: Optional[int] = None
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class ChapterResponse(ChapterBase):
    # DB primary key is integer; novel_id references UUID string
    id: int
    novel_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
