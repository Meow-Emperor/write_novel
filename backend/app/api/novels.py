from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from ..core.database import get_db
from ..core.dependencies import get_current_user_or_demo
from ..core.logger import logger
from ..models.novel import Novel, NovelBlueprint
from ..models.user import User
from ..schemas.novel import NovelCreate, NovelResponse, NovelUpdate

router = APIRouter(prefix="/api/novels", tags=["novels"])


def _build_response(novel: Novel) -> NovelResponse:
    """Assemble a NovelResponse, merging blueprint fields for backward compat."""
    author = None
    genre = None
    description = None
    if getattr(novel, "blueprint", None):
        # 将蓝图中的字段映射为响应中的兼容字段
        genre = novel.blueprint.genre
        # description 兼容：优先使用 full_synopsis，其次 one_sentence_summary
        description = novel.blueprint.full_synopsis or novel.blueprint.one_sentence_summary
        # author 放置在 world_setting JSON 中进行兼容
        try:
            if novel.blueprint.world_setting and isinstance(novel.blueprint.world_setting, dict):
                author = novel.blueprint.world_setting.get("author")
        except Exception:
            author = None

    return NovelResponse(
        id=novel.id,
        user_id=novel.user_id,
        title=novel.title,
        initial_prompt=novel.initial_prompt,
        status=novel.status.upper() if novel.status else "DRAFT",
        created_at=novel.created_at,
        updated_at=novel.updated_at,
        author=author,
        genre=genre,
        description=description,
    )


# Accept both with and without trailing slash for better DX
@router.get("/", response_model=List[NovelResponse])
@router.get("", response_model=List[NovelResponse])
async def list_novels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of novels."""
    try:
        logger.info(f"Fetching novels with skip={skip}, limit={limit}")
        novels = (
            db.query(Novel)
            .options(
                selectinload(Novel.blueprint),
            )
            .order_by(Novel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.info(f"Retrieved {len(novels)} novels")
        return [_build_response(n) for n in novels]
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_novels: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single novel by its identifier."""
    try:
        logger.info(f"Fetching novel with id={novel_id}")
        novel = (
            db.query(Novel)
            .options(
                selectinload(Novel.characters),
                selectinload(Novel.chapters),
                selectinload(Novel.plots),
                selectinload(Novel.blueprint),
            )
            .filter(Novel.id == str(novel_id))
            .first()
        )
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_novel: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not novel:
        logger.warning(f"Novel not found: {novel_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    
    logger.info(f"Retrieved novel: {novel.title}")
    return _build_response(novel)


@router.post("/", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def create_novel(
    payload: NovelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_demo),
):
    """Create a new novel entry."""
    try:
        logger.info(f"Creating novel: {payload.title}")
        # 从当前用户中写入 user_id，忽略外部传入的 user_id
        novel = Novel(
            title=payload.title,
            initial_prompt=payload.initial_prompt,
            status=(payload.status or "DRAFT").lower(),
            user_id=current_user.id,
        )
        db.add(novel)
        db.flush()

        # 兼容旧字段：如果传入 genre 或 description，则创建/更新蓝图
        if payload.genre or payload.description or payload.author:
            bp = (
                db.query(NovelBlueprint)
                .filter(NovelBlueprint.novel_id == novel.id)
                .first()
            )
            if not bp:
                bp = NovelBlueprint(novel_id=novel.id)
                db.add(bp)
            if payload.genre:
                bp.genre = payload.genre
            if payload.description:
                # 存入 full_synopsis 字段，保留信息完整性
                bp.full_synopsis = payload.description
            if payload.author:
                # 将 author 以兼容形式存入 world_setting JSON
                existing = bp.world_setting or {}
                if not isinstance(existing, dict):
                    existing = {}
                existing.update({"author": payload.author})
                bp.world_setting = existing

        db.commit()
        db.refresh(novel)
        logger.info(f"Novel created successfully: {novel.id}")
        return _build_response(novel)
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_novel: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{novel_id}", response_model=NovelResponse)
async def update_novel(novel_id: UUID, payload: NovelUpdate, db: Session = Depends(get_db)):
    """Update an existing novel."""
    try:
        logger.info(f"Updating novel: {novel_id}")
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
        if not novel:
            logger.warning(f"Novel not found for update: {novel_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

        update_data = payload.model_dump(exclude_unset=True)
        logger.debug(f"Update data: {update_data}")
        for field, value in update_data.items():
            setattr(novel, field, value)

        db.commit()
        db.refresh(novel)
        logger.info(f"Novel updated successfully: {novel_id}")
        return _build_response(novel)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in update_novel: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{novel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_novel(novel_id: UUID, db: Session = Depends(get_db)):
    """Delete a novel by identifier."""
    try:
        logger.info(f"Deleting novel: {novel_id}")
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
        if not novel:
            logger.warning(f"Novel not found for deletion: {novel_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

        db.delete(novel)
        db.commit()
        logger.info(f"Novel deleted successfully: {novel_id}")
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in delete_novel: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
