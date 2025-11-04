"""
AI服务数据传输对象(DTO)模式
定义AI生成内容和模型配置的API数据结构
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class AIGenerateRequest(BaseModel):
    """AI内容生成请求模式"""
    novel_id: UUID  # 关联的小说ID
    chapter_id: Optional[UUID] = None  # 关联的章节ID（可选）
    section_id: Optional[UUID] = None  # 关联的段落ID（可选）
    prompt: str  # 用户提示词/需求描述
    context_type: str  # 上下文类型：character(角色), world(世界观), plot(情节), content(内容)
    max_tokens: Optional[int] = 2000  # 生成的最大token数
    # AI配置（可选，未提供则使用环境变量默认值）
    provider: Optional[str] = "openai"  # AI提供商：openai, anthropic, custom
    base_url: Optional[str] = None  # 自定义API端点URL
    api_key: Optional[str] = None  # API密钥
    model_name: Optional[str] = "gpt-4"  # 模型名称


class AIGenerateResponse(BaseModel):
    """AI内容生成响应模式"""
    content: str  # 生成的内容
    tokens_used: int  # 使用的token数量
    model: str  # 使用的模型名称


class AIModelConfigBase(BaseModel):
    """AI模型配置基础模式"""
    provider: str  # 提供商：openai, anthropic, custom
    base_url: Optional[str] = None  # API端点URL
    api_key: str  # API密钥
    model_name: str  # 模型名称
    fallback_provider: Optional[str] = None  # 备用提供商


class AIModelConfigCreate(AIModelConfigBase):
    """AI模型配置创建模式"""
    pass


class AIModelConfigResponse(AIModelConfigBase):
    """AI模型配置响应模式"""
    id: UUID  # 配置ID
    created_at: datetime  # 创建时间

    class Config:
        from_attributes = True  # 允许从ORM模型属性读取数据
