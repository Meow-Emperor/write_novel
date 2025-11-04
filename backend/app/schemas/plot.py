from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PlotBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    act: Optional[str] = Field(None, max_length=50)
    key_events: Optional[str] = None
    characters: Optional[str] = None
    conflicts: Optional[str] = None
    order: int = Field(default=0)


class PlotCreate(PlotBase):
    novel_id: UUID


class PlotUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    act: Optional[str] = Field(None, max_length=50)
    key_events: Optional[str] = None
    characters: Optional[str] = None
    conflicts: Optional[str] = None
    order: Optional[int] = None


class PlotResponse(PlotBase):
    id: UUID
    novel_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
