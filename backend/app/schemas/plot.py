from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PlotBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    plot_type: Optional[str] = Field(None, max_length=50)
    order: int = Field(default=0)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class PlotCreate(PlotBase):
    novel_id: UUID


class PlotUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    plot_type: Optional[str] = Field(None, max_length=50)
    order: Optional[int] = None
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class PlotResponse(PlotBase):
    id: UUID
    novel_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
