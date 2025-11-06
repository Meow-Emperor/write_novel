from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorldSettingBase(BaseModel):
    era: Optional[str] = Field(None, max_length=100, description="时代背景")
    locations: Optional[dict[str, Any]] = Field(None, description="地点设定")
    rules: Optional[dict[str, Any]] = Field(None, description="世界规则")
    culture: Optional[dict[str, Any]] = Field(None, description="文化设定")


class WorldSettingCreate(WorldSettingBase):
    novel_id: UUID


class WorldSettingUpdate(BaseModel):
    era: Optional[str] = Field(None, max_length=100)
    locations: Optional[dict[str, Any]] = None
    rules: Optional[dict[str, Any]] = None
    culture: Optional[dict[str, Any]] = None


class WorldSettingResponse(WorldSettingBase):
    id: int
    novel_id: str
    created_at: datetime

    class Config:
        from_attributes = True
