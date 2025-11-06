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
    # Novel uses UUID string identifiers; accept UUID here and map to str in routes
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
    # Character primary key is an integer in the DB model
    id: int
    # Novel foreign key is a UUID string
    novel_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
