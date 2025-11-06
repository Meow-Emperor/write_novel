from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PromptBase(BaseModel):
    name: str
    title: Optional[str] = None
    content: str
    tags: Optional[str] = None


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None


class PromptResponse(PromptBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
