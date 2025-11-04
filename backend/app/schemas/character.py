from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CharacterBase(BaseModel):
    name: str = Field(..., max_length=100)
    role: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    appearance: Optional[str] = None
    relationships: Optional[str] = None


class CharacterCreate(CharacterBase):
    novel_id: UUID


class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    appearance: Optional[str] = None
    relationships: Optional[str] = None


class CharacterResponse(CharacterBase):
    id: UUID
    novel_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
