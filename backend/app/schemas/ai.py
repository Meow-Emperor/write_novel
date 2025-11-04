from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class AIGenerateRequest(BaseModel):
    novel_id: UUID
    chapter_id: Optional[UUID] = None
    section_id: Optional[UUID] = None
    prompt: str
    context_type: str  # character, world, plot, content
    max_tokens: Optional[int] = 2000
    # AI configuration (optional, uses env defaults if not provided)
    provider: Optional[str] = "openai"  # openai, anthropic, custom
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4"


class AIGenerateResponse(BaseModel):
    content: str
    tokens_used: int
    model: str


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
