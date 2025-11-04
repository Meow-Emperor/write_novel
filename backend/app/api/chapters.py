from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..models.chapter import Chapter
from ..schemas.chapter import ChapterCreate, ChapterResponse, ChapterUpdate

router = APIRouter(prefix="/api/chapters", tags=["chapters"])


@router.get("/", response_model=List[ChapterResponse])
async def list_chapters(novel_id: UUID = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of chapters."""
    try:
        logger.info(f"Fetching chapters with novel_id={novel_id}, skip={skip}, limit={limit}")
        query = db.query(Chapter)
        if novel_id:
            query = query.filter(Chapter.novel_id == str(novel_id))
        chapters = query.order_by(Chapter.chapter_number).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(chapters)} chapters")
        return chapters
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_chapters: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(chapter_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single chapter by its identifier."""
    try:
        logger.info(f"Fetching chapter with id={chapter_id}")
        chapter = db.query(Chapter).filter(Chapter.id == str(chapter_id)).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_chapter: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not chapter:
        logger.warning(f"Chapter not found: {chapter_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    
    logger.info(f"Retrieved chapter: {chapter.title}")
    return chapter


@router.post("/", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(payload: ChapterCreate, db: Session = Depends(get_db)):
    """Create a new chapter entry."""
    try:
        logger.info(f"Creating chapter: {payload.title}")
        chapter = Chapter(**payload.model_dump())
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
        logger.info(f"Chapter created successfully: {chapter.id}")
        return chapter
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_chapter: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(chapter_id: UUID, payload: ChapterUpdate, db: Session = Depends(get_db)):
    """Update an existing chapter."""
    try:
        logger.info(f"Updating chapter: {chapter_id}")
        chapter = db.query(Chapter).filter(Chapter.id == str(chapter_id)).first()
        if not chapter:
            logger.warning(f"Chapter not found for update: {chapter_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

        update_data = payload.model_dump(exclude_unset=True)
        logger.debug(f"Update data: {update_data}")
        for field, value in update_data.items():
            setattr(chapter, field, value)

        db.commit()
        db.refresh(chapter)
        logger.info(f"Chapter updated successfully: {chapter_id}")
        return chapter
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in update_chapter: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(chapter_id: UUID, db: Session = Depends(get_db)):
    """Delete a chapter by identifier."""
    try:
        logger.info(f"Deleting chapter: {chapter_id}")
        chapter = db.query(Chapter).filter(Chapter.id == str(chapter_id)).first()
        if not chapter:
            logger.warning(f"Chapter not found for deletion: {chapter_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

        db.delete(chapter)
        db.commit()
        logger.info(f"Chapter deleted successfully: {chapter_id}")
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in delete_chapter: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
