from typing import Optional

from pydantic import BaseModel


class SystemConfigBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfigUpdate(BaseModel):
    value: str
    description: Optional[str] = None


class SystemConfigResponse(SystemConfigBase):
    class Config:
        from_attributes = True
