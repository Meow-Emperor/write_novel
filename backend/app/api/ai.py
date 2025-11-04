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

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _build_context(db: Session, novel_id: UUID) -> Dict[str, Any]:
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
    try:
        context = _build_context(db, payload.novel_id)
        service = AIService(
            provider=payload.provider or "openai",
            base_url=payload.base_url,
            api_key=payload.api_key,
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(payload.prompt, context, max_tokens=payload.max_tokens or 2000)
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
