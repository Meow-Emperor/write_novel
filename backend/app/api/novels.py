from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..models.novel import Novel
from ..schemas.novel import NovelCreate, NovelResponse, NovelUpdate

router = APIRouter(prefix="/api/novels", tags=["novels"])


@router.get("/", response_model=List[NovelResponse])
async def list_novels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of novels."""
    try:
        logger.info(f"Fetching novels with skip={skip}, limit={limit}")
        novels = db.query(Novel).order_by(Novel.created_at.desc()).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(novels)} novels")
        return novels
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_novels: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single novel by its identifier."""
    try:
        logger.info(f"Fetching novel with id={novel_id}")
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_novel: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not novel:
        logger.warning(f"Novel not found: {novel_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    
    logger.info(f"Retrieved novel: {novel.title}")
    return novel


@router.post("/", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def create_novel(payload: NovelCreate, db: Session = Depends(get_db)):
    """Create a new novel entry."""
    try:
        logger.info(f"Creating novel: {payload.title}")
        novel = Novel(**payload.model_dump())
        db.add(novel)
        db.commit()
        db.refresh(novel)
        logger.info(f"Novel created successfully: {novel.id}")
        return novel
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
        return novel
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
