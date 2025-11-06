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
from ..models.world import WorldSetting
from ..schemas.ai import (
    AICharacterGenerateRequest,
    AIChapterOutlineRequest,
    AIContentExpandRequest,
    AIGenerateRequest,
    AIGenerateResponse,
    AIPlotGenerateRequest,
    AIWorldGenerateRequest,
    AITestRequest,
    AITestResponse,
)
from ..services.ai_service import AIService
from ..core.config import settings

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _build_context(db: Session, novel_id: UUID, include_characters: bool = False, include_plots: bool = False, include_world: bool = False) -> Dict[str, Any]:
    try:
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    # Pull genre/description from blueprint for compatibility
    blueprint = getattr(novel, "blueprint", None)
    description = None
    genre = None
    if blueprint is not None:
        genre = getattr(blueprint, "genre", None)
        description = getattr(blueprint, "full_synopsis", None) or getattr(blueprint, "one_sentence_summary", None)

    context = {
        "novel": {
            "id": novel.id,
            "title": novel.title,
            "genre": genre,
            "description": description,
        }
    }
    
    if include_characters:
        characters = db.query(Character).filter(Character.novel_id == str(novel_id)).all()
        context["characters"] = [
            {
                "name": c.name,
                "role": getattr(c, "identity", None),
                "description": (c.extra or {}).get("description") if isinstance(getattr(c, "extra", None), dict) else None,
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
                # 兼容旧字段命名，模型中无 plot_type，使用 act 作为类型/幕次信息
                "type": getattr(p, "act", None),
                "act": getattr(p, "act", None),
                "key_events": getattr(p, "key_events", None),
            }
            for p in plots
        ]
    
    if include_world:
        world = db.query(WorldSetting).filter(WorldSetting.novel_id == str(novel_id)).first()
        if world:
            context["world"] = {
                "era": world.era,
                "rules": world.rules,
                "locations": world.locations,
                "culture": world.culture,
            }
    
    return context


@router.post("/generate", response_model=AIGenerateResponse)
async def generate_content(payload: AIGenerateRequest, db: Session = Depends(get_db)):
    """General AI content generation endpoint."""
    logger.info(f"AI generation request for novel {payload.novel_id} with provider {payload.provider}")
    try:
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True, include_world=True)
        service = AIService(
            provider=payload.provider or "openai",
            base_url=getattr(payload, "base_url", None),
            api_key=getattr(payload, "api_key", None),
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(payload.prompt, context, max_tokens=payload.max_tokens or 2000, temperature=payload.temperature)
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
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True, include_world=True)
        
        prompt = f"""Create a detailed character profile for a {payload.character_role} in this novel.
Genre: {context['novel']['genre']}
Novel Description: {context['novel']['description']}

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
            base_url=getattr(payload, "base_url", None),
            api_key=getattr(payload, "api_key", None),
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=1500, temperature=payload.temperature)
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
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True, include_world=True)
        
        length_guidance = {
            "short": "3-5 key plot points",
            "medium": "7-10 key plot points with development",
            "long": "detailed plot with 12-15 plot points and subplots"
        }
        
        prompt = f"""Create a {payload.plot_type} plot for this novel.
Genre: {context['novel']['genre']}
Novel Description: {context['novel']['description']}

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
            base_url=getattr(payload, "base_url", None),
            api_key=getattr(payload, "api_key", None),
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=2000, temperature=payload.temperature)
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
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True, include_world=True)
        
        existing_chapters = db.query(Chapter).filter(
            Chapter.novel_id == str(payload.novel_id),
            Chapter.chapter_number < payload.chapter_number
        ).order_by(Chapter.chapter_number).all()

        previous_summary = (
            "\n".join([
                f"Chapter {c.chapter_number}: {c.title or ''} - {c.real_summary or ''}"
                for c in existing_chapters[-3:]
            ]) if existing_chapters else "This is the first chapter."
        )
        
        prompt = f"""Create a detailed outline for Chapter {payload.chapter_number} of this novel.

Genre: {context['novel']['genre']}
Novel Description: {context['novel']['description']}

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
            base_url=getattr(payload, "base_url", None),
            api_key=getattr(payload, "api_key", None),
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=1800, temperature=payload.temperature)
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
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True, include_world=True)
        
        chapter = None
        if payload.chapter_id is not None:
            # Chapter IDs are integers; allow flexible matching
            cid_raw = str(payload.chapter_id)
            try:
                cid_int = int(cid_raw)
                chapter = db.query(Chapter).filter(Chapter.id == cid_int).first()
            except ValueError:
                # Not an int-like ID; skip lookup without failing the request
                chapter = None
        
        style_guidance = {
            "brief": "concise and to the point, expanding with essential details only",
            "detailed": "rich with descriptive language, sensory details, and character insights",
            "dramatic": "tension-filled, emotionally charged, with vivid imagery"
        }
        
        chapter_title = chapter.title if chapter else "(current chapter)"
        prompt = f"""Expand the following content snippet in a {payload.expansion_style} style.

Genre: {context['novel']['genre']}
Chapter: {chapter_title}
Style: {style_guidance.get(payload.expansion_style, 'detailed')}

Content Snippet to Expand:
{payload.content_snippet}

Please expand this snippet maintaining consistency with the story's tone and genre. 
Add descriptive details, character emotions, dialogue if appropriate, and sensory information.
Target expansion: 2-3x the original length."""

        service = AIService(
            provider=payload.provider or "openai",
            base_url=getattr(payload, "base_url", None),
            api_key=getattr(payload, "api_key", None),
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=1600, temperature=payload.temperature)
        logger.info(f"Content expansion completed, tokens used: {result.get('tokens_used', 0)}")
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Content expansion error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/generate-world", response_model=AIGenerateResponse)
async def generate_world(payload: AIWorldGenerateRequest, db: Session = Depends(get_db)):
    """Generate or enhance world settings using AI."""
    logger.info(f"AI world generation for novel {payload.novel_id}")
    try:
        context = _build_context(db, payload.novel_id, include_characters=True, include_plots=True, include_world=True)

        focus_text = "overall"
        if payload.focus in {"era", "rules", "locations", "culture"}:
            focus_text = payload.focus

        prompt = f"""You are assisting a novelist in worldbuilding. Based on the context, generate detailed content for {focus_text}.

If world settings already exist, expand and refine them while maintaining consistency.

Please include clear sections and, where appropriate, structured bullet points and concise JSON examples. Cover:
1. Era / Time Period and historical backdrop
2. Foundational Rules (physics/magic/societal laws)
3. Key Locations (names, descriptions, significance)
4. Culture (customs, beliefs, languages, technology)
5. How the world constraints and opportunities impact characters and plot

Provide actionable details suitable for immediate writing."""

        service = AIService(
            provider=payload.provider or "openai",
            base_url=getattr(payload, "base_url", None),
            api_key=getattr(payload, "api_key", None),
            model_name=payload.model_name or "gpt-4",
        )
        result = await service.generate(prompt, context, max_tokens=2000, temperature=payload.temperature)
        logger.info(f"World generation completed, tokens used: {result.get('tokens_used', 0)}")
        return AIGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(f"World generation error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/test-config", response_model=AITestResponse)
async def test_ai_config(payload: AITestRequest):
    """Test AI provider connectivity and credentials without generating content."""
    logger.info(f"Testing AI config for provider={payload.provider}")
    try:
        # Development fallback: if in DEBUG and no key provided, return OK to avoid blocking UI
        if settings.DEBUG:
            prov_lower = (payload.provider or "openai").lower()
            key = (payload.api_key or (settings.OPENAI_API_KEY if prov_lower == "openai" else settings.ANTHROPIC_API_KEY) or "").strip()
            if not key or key.lower().startswith("your-"):
                return AITestResponse(ok=True, provider=prov_lower, message="开发模式：未配置密钥，使用模拟连接成功")
        prov = (payload.provider or "openai").lower()
        if prov == "openai":
            try:
                from openai import AsyncOpenAI  # type: ignore
            except ImportError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OpenAI SDK 未安装") from e
            client = AsyncOpenAI(api_key=payload.api_key or settings.OPENAI_API_KEY, base_url=payload.base_url)
            # List models as a lightweight auth check
            await client.models.list()
            return AITestResponse(ok=True, provider=prov, message="OpenAI 连接成功")
        elif prov == "anthropic":
            try:
                from anthropic import AsyncAnthropic  # type: ignore
            except ImportError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Anthropic SDK 未安装") from e
            client = AsyncAnthropic(api_key=payload.api_key or settings.ANTHROPIC_API_KEY, base_url=payload.base_url)
            # List models to verify
            await client.models.list()
            return AITestResponse(ok=True, provider=prov, message="Anthropic 连接成功")
        else:
            # Assume OpenAI-compatible custom endpoint
            import httpx
            if not payload.base_url:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="自定义 provider 需要提供 base_url")
            models_url = payload.base_url.rstrip("/")
            if not models_url.endswith("/models"):
                if not models_url.endswith("/v1"):
                    models_url = models_url + "/v1"
                models_url = models_url + "/models"
            headers = {}
            if payload.api_key:
                headers["Authorization"] = f"Bearer {payload.api_key}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(models_url, headers=headers)
                if resp.status_code != 200:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"HTTP {resp.status_code}: {resp.text}")
            return AITestResponse(ok=True, provider=prov, message="自定义接口连接成功")
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(f"AI config test error: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc




