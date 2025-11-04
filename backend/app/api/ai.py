"""
AI辅助写作API路由
提供AI内容生成接口
"""
from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.novel import Novel
from ..schemas.ai import AIGenerateRequest, AIGenerateResponse
from ..services.ai_service import AIService

# 创建AI路由器，前缀为/api/ai
router = APIRouter(prefix="/api/ai", tags=["ai"])


def _build_context(db: Session, novel_id: UUID) -> Dict[str, Any]:
    """
    构建AI生成所需的上下文信息
    
    Args:
        db: 数据库会话
        novel_id: 小说UUID
        
    Returns:
        包含小说信息的上下文字典
        
    Raises:
        404: 小说不存在
        500: 数据库错误
    """
    try:
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    return {
        "novel": {
            "id": novel.id,
            "title": novel.title,
            "genre": novel.genre,
            "synopsis": novel.description,
        }
    }


@router.post("/generate", response_model=AIGenerateResponse)
async def generate_content(payload: AIGenerateRequest, db: Session = Depends(get_db)):
    """
    使用AI生成内容
    
    Args:
        payload: AI生成请求数据，包含提示词、上下文类型、模型配置等
        db: 数据库会话（依赖注入）
        
    Returns:
        生成的内容、token使用量和模型信息
        
    Raises:
        404: 小说不存在
        500: AI服务错误或数据库错误
    """
    try:
        # 构建上下文信息
        context = _build_context(db, payload.novel_id)
        
        # 创建AI服务实例
        service = AIService(
            provider=payload.provider or "openai",
            base_url=payload.base_url,
            api_key=payload.api_key,
            model_name=payload.model_name or "gpt-4",
        )
        
        # 调用AI生成内容
        result = await service.generate(payload.prompt, context, max_tokens=payload.max_tokens or 2000)
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
