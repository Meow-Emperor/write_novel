from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============= ChapterVersion Schemas =============

class ChapterVersionBase(BaseModel):
    version_label: Optional[str] = None
    provider: Optional[str] = None
    content: str = Field(..., min_length=1)


class ChapterVersionCreate(ChapterVersionBase):
    chapter_id: int


class ChapterVersionResponse(ChapterVersionBase):
    id: int
    chapter_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= ChapterEvaluation Schemas =============

class ChapterEvaluationBase(BaseModel):
    decision: Optional[str] = Field(None, max_length=32)
    feedback: Optional[str] = None
    score: Optional[float] = Field(None, ge=0, le=10)


class ChapterEvaluationCreate(ChapterEvaluationBase):
    chapter_id: int
    version_id: Optional[int] = None


class ChapterEvaluationResponse(ChapterEvaluationBase):
    id: int
    chapter_id: int
    version_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Extended Chapter Response with Versions =============

class ChapterWithVersionsResponse(BaseModel):
    """章节详情，包含版本列表"""
    id: int
    novel_id: str
    chapter_number: int
    title: Optional[str]
    summary: Optional[str]
    word_count: int
    status: str
    selected_version_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    # 版本列表
    versions: list[ChapterVersionResponse] = []
    # 当前选中版本
    selected_version: Optional[ChapterVersionResponse] = None
    # 评估记录
    evaluations: list[ChapterEvaluationResponse] = []

    class Config:
        from_attributes = True
