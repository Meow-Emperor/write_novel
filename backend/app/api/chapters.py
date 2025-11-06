from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..models.chapter import Chapter
from ..schemas.chapter import ChapterCreate, ChapterResponse, ChapterUpdate

router = APIRouter(prefix="/api/chapters", tags=["chapters"])


@router.get("/", response_model=List[ChapterResponse])
@router.get("", response_model=List[ChapterResponse])
async def list_chapters(novel_id: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of chapters."""
    try:
        logger.info(f"Fetching chapters with novel_id={novel_id}, skip={skip}, limit={limit}")
        query = db.query(Chapter)
        if novel_id:
            query = query.filter(Chapter.novel_id == str(novel_id))
        chapters = query.order_by(Chapter.chapter_number).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(chapters)} chapters")
        return [
            ChapterResponse(
                id=c.id,
                novel_id=c.novel_id,
                title=c.title or "",
                chapter_number=c.chapter_number,
                summary=c.real_summary,
                content=c.outline,
                word_count=c.word_count,
                status=c.status.upper() if c.status else "DRAFT",
                notes=None,
                created_at=c.created_at,
                updated_at=c.updated_at,
            ) for c in chapters
        ]
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_chapters: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """Retrieve a single chapter by its identifier."""
    try:
        logger.info(f"Fetching chapter with id={chapter_id}")
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_chapter: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not chapter:
        logger.warning(f"Chapter not found: {chapter_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    
    logger.info(f"Retrieved chapter: {chapter.title}")
    return ChapterResponse(
        id=chapter.id,
        novel_id=chapter.novel_id,
        title=chapter.title or "",
        chapter_number=chapter.chapter_number,
        summary=chapter.real_summary,
        content=chapter.outline,
        word_count=chapter.word_count,
        status=chapter.status.upper() if chapter.status else "DRAFT",
        notes=None,
        created_at=chapter.created_at,
        updated_at=chapter.updated_at,
    )


@router.post("/", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(payload: ChapterCreate, db: Session = Depends(get_db)):
    """Create a new chapter entry."""
    try:
        logger.info(f"Creating chapter: {payload.title}")
        data = payload.model_dump()
        chapter = Chapter(
            novel_id=str(data['novel_id']),
            chapter_number=data['chapter_number'],
            title=data.get('title'),
            outline=data.get('content'),
            real_summary=data.get('summary'),
            status=(data.get('status') or 'DRAFT').lower(),
            word_count=data.get('word_count') or 0,
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
        logger.info(f"Chapter created successfully: {chapter.id}")
        return ChapterResponse(
            id=chapter.id,
            novel_id=chapter.novel_id,
            title=chapter.title or "",
            chapter_number=chapter.chapter_number,
            summary=chapter.real_summary,
            content=chapter.outline,
            word_count=chapter.word_count,
            status=chapter.status,
            notes=None,
            created_at=chapter.created_at,
            updated_at=chapter.updated_at,
        )
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_chapter: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(chapter_id: int, payload: ChapterUpdate, db: Session = Depends(get_db)):
    """Update an existing chapter."""
    try:
        logger.info(f"Updating chapter: {chapter_id}")
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            logger.warning(f"Chapter not found for update: {chapter_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

        update_data = payload.model_dump(exclude_unset=True)
        logger.debug(f"Update data: {update_data}")
        if 'title' in update_data:
            chapter.title = update_data['title']
        if 'chapter_number' in update_data:
            chapter.chapter_number = update_data['chapter_number']
        if 'summary' in update_data:
            chapter.real_summary = update_data['summary']
        if 'content' in update_data:
            chapter.outline = update_data['content']
        if 'word_count' in update_data:
            chapter.word_count = update_data['word_count']
        if 'status' in update_data:
            chapter.status = update_data['status'].lower() if update_data['status'] else 'draft'

        db.commit()
        db.refresh(chapter)
        logger.info(f"Chapter updated successfully: {chapter_id}")
        return ChapterResponse(
            id=chapter.id,
            novel_id=chapter.novel_id,
            title=chapter.title or "",
            chapter_number=chapter.chapter_number,
            summary=chapter.real_summary,
            content=chapter.outline,
            word_count=chapter.word_count,
            status=chapter.status.upper() if chapter.status else "DRAFT",
            notes=None,
            created_at=chapter.created_at,
            updated_at=chapter.updated_at,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in update_chapter: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """Delete a chapter by identifier."""
    try:
        logger.info(f"Deleting chapter: {chapter_id}")
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
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
