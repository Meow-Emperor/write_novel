from typing import Optional

from pydantic import BaseModel


class LLMConfigBase(BaseModel):
    llm_provider_url: Optional[str] = None
    llm_provider_api_key: Optional[str] = None
    llm_provider_model: Optional[str] = None


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigUpdate(LLMConfigBase):
    pass


class LLMConfigResponse(LLMConfigBase):
    user_id: int

    class Config:
        from_attributes = True
