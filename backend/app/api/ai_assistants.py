from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..services.ai_assistants import AssistantFactory
from ..api.ai import _build_context

router = APIRouter(prefix="/api/ai-assistants", tags=["ai-assistants"])


# ============= Schemas =============


class AssistantRequest(BaseModel):
    """AI助手请求"""
    role: str = Field(..., description="助手角色")
    novel_id: str = Field(..., description="小说ID")
    user_input: str = Field(..., description="用户输入")
    provider: str = Field(default="openai", description="AI提供商")
    model_name: str = Field(default="gpt-4", description="模型名称")
    base_url: str | None = Field(default=None, description="自定义API地址")
    api_key: str | None = Field(default=None, description="API密钥")
    temperature: float = Field(default=0.7, ge=0, le=2, description="创造性温度")
    max_tokens: int = Field(default=2000, ge=100, le=4000, description="最大token数")


class AssistantResponse(BaseModel):
    """AI助手响应"""
    role: str
    content: str
    tokens_used: int = 0


class AssistantInfo(BaseModel):
    """助手信息"""
    role: str
    name: str
    description: str


# ============= API Endpoints =============


@router.get("/", response_model=List[AssistantInfo])
async def list_assistants():
    """获取所有可用的AI助手列表"""
    try:
        assistants = AssistantFactory.list_assistants()
        return assistants
    except Exception as exc:
        logger.error(f"Error listing assistants: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        ) from exc


@router.post("/generate", response_model=AssistantResponse)
async def generate_with_assistant(
    payload: AssistantRequest,
    db: Session = Depends(get_db)
):
    """使用指定的AI助手生成内容"""
    try:
        logger.info(f"Generating content with assistant role={payload.role} for novel={payload.novel_id}")

        # 构建上下文
        context = _build_context(
            db,
            payload.novel_id,
            include_characters=True,
            include_plots=True,
            include_world=True
        )

        # 创建助手
        assistant = AssistantFactory.create(
            role=payload.role,
            provider=payload.provider,
            model_name=payload.model_name,
            base_url=payload.base_url,
            api_key=payload.api_key,
            temperature=payload.temperature,
        )

        # 生成内容
        content = await assistant.process(
            context=context,
            user_input=payload.user_input,
            max_tokens=payload.max_tokens
        )

        logger.info(f"Content generated successfully with role={payload.role}")

        return AssistantResponse(
            role=payload.role,
            content=content,
            tokens_used=0  # TODO: 从AI服务获取实际token使用量
        )

    except ValueError as exc:
        logger.error(f"Invalid assistant role: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        logger.error(f"Error generating with assistant: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        ) from exc


@router.post("/generate-multiple", response_model=Dict[str, Any])
async def generate_multiple_versions(
    payload: AssistantRequest,
    num_versions: int = 2,
    db: Session = Depends(get_db)
):
    """使用Novelist助手生成多个版本"""
    try:
        if payload.role != "novelist":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multiple versions only supported for 'novelist' role"
            )

        logger.info(f"Generating {num_versions} versions for novel={payload.novel_id}")

        # 构建上下文
        context = _build_context(
            db,
            payload.novel_id,
            include_characters=True,
            include_plots=True,
            include_world=True
        )

        # 创建小说家助手
        assistant = AssistantFactory.create(
            role="novelist",
            provider=payload.provider,
            model_name=payload.model_name,
            base_url=payload.base_url,
            api_key=payload.api_key,
            temperature=payload.temperature,
        )

        # 生成多个版本
        versions = await assistant.process_multiple_versions(
            context=context,
            user_input=payload.user_input,
            num_versions=num_versions
        )

        logger.info(f"Generated {len(versions)} versions successfully")

        return {
            "role": "novelist",
            "versions": versions,
            "count": len(versions)
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error generating multiple versions: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        ) from exc
