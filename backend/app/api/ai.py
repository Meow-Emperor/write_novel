from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..models.chapter import Chapter
from ..models.character import Character
from ..models.novel import Novel
from ..models.plot import Plot
from ..schemas.ai import (
    AICharacterGenerateRequest,
    AIChapterOutlineRequest,
    AIContentExpandRequest,
    AIGenerateRequest,
    AIGenerateResponse,
    AIPlotGenerateRequest,
)
from ..services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _build_context(db: Session, novel_id: UUID, include_characters: bool = False, include_plots: bool = False) -> Dict[str, Any]:
    try:
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    context = {
        "novel": {
            "id": novel.id,
            "title": novel.title,
            "genre": novel.genre,
            "synopsis": novel.description,
        }
    }
    
    if include_characters:
        characters = db.query(Character).filter(Character.novel_id == str(novel_id)).all()
        context["characters"] = [
            {
                "name": c.name,
                "role": c.role,
                "description": c.description,
                "personality": c.personality,
            }
            for c in characters
        ]
    
    if include_plots:
        plots = db.query(Plot).filter(Plot.novel_id == str(novel_id)).order_by(Plot.order).all()
        context["plots"] = [
            {
                "title": p.title,
                "description": p.description,
                "type": p.plot_type,
            }
            for p in plots
        ]
    
    return context


@router.post("/generate", response_model=AIGenerateResponse)
async def generate_content(payload: AIGenerateRequest, db: Session = Depends(get_db)):
    """General AI content generation endpoint."""
    logger.info(f"AI generation request for novel {payload.novel_id} with provider {payload.provider}")
    try:
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True)
        service = AIService(
            provider=payload.provider or "openai",
            base_url=payload.base_url,
            api_key=payload.api_key,
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(payload.prompt, context, max_tokens=payload.max_tokens or 2000)
        logger.info(f"AI generation completed, tokens used: {result.get('tokens_used', 0)}")
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(f"AI generation error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/generate-character", response_model=AIGenerateResponse)
async def generate_character(payload: AICharacterGenerateRequest, db: Session = Depends(get_db)):
    """Generate a character profile using AI."""
    logger.info(f"AI character generation for novel {payload.novel_id}")
    try:
        context = _build_context(db, payload.novel_id, include_characters=True)
        
        prompt = f"""Create a detailed character profile for a {payload.character_role} in this novel.
Genre: {context['novel']['genre']}
Novel Synopsis: {context['novel']['synopsis']}

{"Additional traits: " + payload.character_traits if payload.character_traits else ""}

Please provide:
1. Character Name
2. Role: {payload.character_role}
3. Physical Appearance
4. Personality Traits
5. Background Story
6. Motivations and Goals
7. Character Arc Potential
8. Relationships with other characters (if any exist)

Format the response clearly with these sections."""

        service = AIService(
            provider=payload.provider or "openai",
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=1500)
        logger.info(f"Character generation completed, tokens used: {result.get('tokens_used', 0)}")
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Character generation error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/generate-plot", response_model=AIGenerateResponse)
async def generate_plot(payload: AIPlotGenerateRequest, db: Session = Depends(get_db)):
    """Generate a plot outline using AI."""
    logger.info(f"AI plot generation for novel {payload.novel_id}")
    try:
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True)
        
        length_guidance = {
            "short": "3-5 key plot points",
            "medium": "7-10 key plot points with development",
            "long": "detailed plot with 12-15 plot points and subplots"
        }
        
        prompt = f"""Create a {payload.plot_type} plot for this novel.
Genre: {context['novel']['genre']}
Novel Synopsis: {context['novel']['synopsis']}

Plot Type: {payload.plot_type}
Length: {payload.plot_length} ({length_guidance.get(payload.plot_length, 'medium development')})

Existing Characters: {', '.join([c['name'] for c in context.get('characters', [])])}

Please provide:
1. Plot Title
2. Plot Type: {payload.plot_type}
3. Main Conflict/Hook
4. Key Plot Points (with chapter suggestions)
5. Character Involvement
6. Resolution/Climax
7. How it ties into the main story

Format the response clearly with these sections."""

        service = AIService(
            provider=payload.provider or "openai",
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=2000)
        logger.info(f"Plot generation completed, tokens used: {result.get('tokens_used', 0)}")
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Plot generation error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/generate-chapter-outline", response_model=AIGenerateResponse)
async def generate_chapter_outline(payload: AIChapterOutlineRequest, db: Session = Depends(get_db)):
    """Generate a chapter outline using AI."""
    logger.info(f"AI chapter outline generation for novel {payload.novel_id}, chapter {payload.chapter_number}")
    try:
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True)
        
        existing_chapters = db.query(Chapter).filter(
            Chapter.novel_id == str(payload.novel_id),
            Chapter.chapter_number < payload.chapter_number
        ).order_by(Chapter.chapter_number).all()
        
        previous_summary = "\n".join([
            f"Chapter {c.chapter_number}: {c.title} - {c.summary}"
            for c in existing_chapters[-3:]  # Last 3 chapters
        ]) if existing_chapters else "This is the first chapter."
        
        prompt = f"""Create a detailed outline for Chapter {payload.chapter_number} of this novel.

Genre: {context['novel']['genre']}
Novel Synopsis: {context['novel']['synopsis']}

Previous Chapters Summary:
{previous_summary}

{"Chapter Theme: " + payload.chapter_theme if payload.chapter_theme else ""}

Characters Available: {', '.join([c['name'] + ' (' + c['role'] + ')' for c in context.get('characters', [])])}

Please provide:
1. Chapter Title
2. Chapter Summary (2-3 sentences)
3. Opening Scene
4. Key Events (3-5 major events in this chapter)
5. Character Development Moments
6. Plot Advancement
7. Cliffhanger/Transition to Next Chapter
8. Estimated Word Count Range

Format the response clearly with these sections."""

        service = AIService(
            provider=payload.provider or "openai",
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=1800)
        logger.info(f"Chapter outline generation completed, tokens used: {result.get('tokens_used', 0)}")
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Chapter outline generation error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/expand-content", response_model=AIGenerateResponse)
async def expand_content(payload: AIContentExpandRequest, db: Session = Depends(get_db)):
    """Expand a content snippet using AI."""
    logger.info(f"AI content expansion for chapter {payload.chapter_id}")
    try:
        context = _build_context(db, payload.novel_id, include_characters=True)
        
        chapter = db.query(Chapter).filter(Chapter.id == str(payload.chapter_id)).first()
        if not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
        
        style_guidance = {
            "brief": "concise and to the point, expanding with essential details only",
            "detailed": "rich with descriptive language, sensory details, and character insights",
            "dramatic": "tension-filled, emotionally charged, with vivid imagery"
        }
        
        prompt = f"""Expand the following content snippet in a {payload.expansion_style} style.

Genre: {context['novel']['genre']}
Chapter: {chapter.title}
Style: {style_guidance.get(payload.expansion_style, 'detailed')}

Content Snippet to Expand:
{payload.content_snippet}

Please expand this snippet maintaining consistency with the story's tone and genre. 
Add descriptive details, character emotions, dialogue if appropriate, and sensory information.
Target expansion: 2-3x the original length."""

        service = AIService(
            provider=payload.provider or "openai",
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=2000)
        logger.info(f"Content expansion completed, tokens used: {result.get('tokens_used', 0)}")
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Content expansion error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
