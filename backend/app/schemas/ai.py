from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class AIGenerateRequest(BaseModel):
    novel_id: UUID
    chapter_id: Optional[UUID] = None
    section_id: Optional[UUID] = None
    prompt: str
    context_type: str  # character, world, plot, content, chapter, outline
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = None
    provider: Optional[str] = "openai"  # openai, anthropic, custom
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4"


class AIGenerateResponse(BaseModel):
    content: str
    tokens_used: int
    model: str


class AICharacterGenerateRequest(BaseModel):
    novel_id: UUID
    character_role: str  # protagonist, antagonist, supporting
    character_traits: Optional[str] = None
    temperature: Optional[float] = None
    provider: Optional[str] = "openai"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4"


class AIPlotGenerateRequest(BaseModel):
    novel_id: UUID
    plot_type: str  # main, subplot, twist
    plot_length: Optional[str] = "medium"  # short, medium, long
    temperature: Optional[float] = None
    provider: Optional[str] = "openai"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4"


class AIChapterOutlineRequest(BaseModel):
    novel_id: UUID
    chapter_number: int
    chapter_theme: Optional[str] = None
    temperature: Optional[float] = None
    provider: Optional[str] = "openai"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4"


class AIContentExpandRequest(BaseModel):
    novel_id: UUID
    # Accept numeric chapter ID (primary key) or string; frontend passes route param string
    chapter_id: Optional[int | str] = None
    content_snippet: str
    expansion_style: Optional[str] = "detailed"  # brief, detailed, dramatic
    temperature: Optional[float] = None
    provider: Optional[str] = "openai"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4"


class AIModelConfigBase(BaseModel):
    provider: str  # openai, anthropic, custom
    base_url: Optional[str] = None
    api_key: str
    model_name: str
    fallback_provider: Optional[str] = None


class AIModelConfigCreate(AIModelConfigBase):
    pass


class AIModelConfigResponse(AIModelConfigBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AIWorldGenerateRequest(BaseModel):
    novel_id: UUID
    focus: Optional[str] = None  # era, rules, locations, culture, or overall
    temperature: Optional[float] = None
    provider: Optional[str] = "openai"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4"


class AITestRequest(BaseModel):
    provider: str  # openai, anthropic, custom
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None


class AITestResponse(BaseModel):
    ok: bool
    provider: str
    message: str
