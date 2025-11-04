from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.novel import Novel
from ..schemas.novel import NovelCreate, NovelResponse, NovelUpdate

router = APIRouter(prefix="/api/novels", tags=["novels"])


@router.get("/", response_model=List[NovelResponse])
async def list_novels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of novels."""
    try:
        novels = db.query(Novel).offset(skip).limit(limit).all()
        return novels
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single novel by its identifier."""
    try:
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    return novel


@router.post("/", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def create_novel(payload: NovelCreate, db: Session = Depends(get_db)):
    """Create a new novel entry."""
    try:
        novel = Novel(**payload.model_dump())
        db.add(novel)
        db.commit()
        db.refresh(novel)
        return novel
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{novel_id}", response_model=NovelResponse)
async def update_novel(novel_id: UUID, payload: NovelUpdate, db: Session = Depends(get_db)):
    """Update an existing novel."""
    try:
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
        if not novel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(novel, field, value)

        db.commit()
        db.refresh(novel)
        return novel
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{novel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_novel(novel_id: UUID, db: Session = Depends(get_db)):
    """Delete a novel by identifier."""
    try:
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
        if not novel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

        db.delete(novel)
        db.commit()
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
