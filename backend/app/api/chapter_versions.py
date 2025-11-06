from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from ..core.database import get_db
from ..core.logger import logger
from ..models.chapter import Chapter, ChapterVersion, ChapterEvaluation
from ..schemas.chapter_version import (
    ChapterVersionCreate,
    ChapterVersionResponse,
    ChapterEvaluationCreate,
    ChapterEvaluationResponse,
    ChapterWithVersionsResponse,
)

router = APIRouter(prefix="/api/chapter-versions", tags=["chapter-versions"])


# ============= Chapter Version Management =============

@router.post("/", response_model=ChapterVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(payload: ChapterVersionCreate, db: Session = Depends(get_db)):
    """创建新的章节版本"""
    try:
        logger.info(f"Creating new version for chapter {payload.chapter_id}")

        # 验证章节存在
        chapter = db.query(Chapter).filter(Chapter.id == payload.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

        # 创建版本
        version = ChapterVersion(
            chapter_id=payload.chapter_id,
            version_label=payload.version_label,
            provider=payload.provider,
            content=payload.content,
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        logger.info(f"Version created successfully: {version.id}")
        return version
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_version: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/chapter/{chapter_id}", response_model=List[ChapterVersionResponse])
async def list_versions(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节的所有版本"""
    try:
        logger.info(f"Fetching versions for chapter {chapter_id}")
        versions = (
            db.query(ChapterVersion)
            .filter(ChapterVersion.chapter_id == chapter_id)
            .order_by(ChapterVersion.created_at.desc())
            .all()
        )
        logger.info(f"Retrieved {len(versions)} versions")
        return versions
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_versions: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{version_id}", response_model=ChapterVersionResponse)
async def get_version(version_id: int, db: Session = Depends(get_db)):
    """获取特定版本详情"""
    try:
        logger.info(f"Fetching version {version_id}")
        version = db.query(ChapterVersion).filter(ChapterVersion.id == version_id).first()
        if not version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
        return version
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_version: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/chapter/{chapter_id}/select/{version_id}", status_code=status.HTTP_200_OK)
async def select_version(chapter_id: int, version_id: int, db: Session = Depends(get_db)):
    """设置章节的当前版本"""
    try:
        logger.info(f"Selecting version {version_id} for chapter {chapter_id}")

        # 验证章节和版本存在
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

        version = db.query(ChapterVersion).filter(
            ChapterVersion.id == version_id,
            ChapterVersion.chapter_id == chapter_id
        ).first()
        if not version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

        # 更新选中的版本
        chapter.selected_version_id = version_id
        # 同时更新章节的内容（可选，保持 outline 字段同步）
        chapter.outline = version.content

        db.commit()
        logger.info(f"Version {version_id} selected for chapter {chapter_id}")
        return {"message": "Version selected successfully", "version_id": version_id}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in select_version: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_version(version_id: int, db: Session = Depends(get_db)):
    """删除特定版本"""
    try:
        logger.info(f"Deleting version {version_id}")
        version = db.query(ChapterVersion).filter(ChapterVersion.id == version_id).first()
        if not version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

        # 检查是否是当前选中的版本
        chapter = db.query(Chapter).filter(
            Chapter.id == version.chapter_id,
            Chapter.selected_version_id == version_id
        ).first()
        if chapter:
            # 如果是当前版本，清空选中
            chapter.selected_version_id = None

        db.delete(version)
        db.commit()
        logger.info(f"Version {version_id} deleted successfully")
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in delete_version: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


# ============= Chapter with Versions =============

@router.get("/chapter/{chapter_id}/with-versions", response_model=ChapterWithVersionsResponse)
async def get_chapter_with_versions(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节详情及其所有版本"""
    try:
        logger.info(f"Fetching chapter {chapter_id} with versions")
        chapter = (
            db.query(Chapter)
            .options(
                selectinload(Chapter.versions),
                selectinload(Chapter.selected_version),
                selectinload(Chapter.evaluations),
            )
            .filter(Chapter.id == chapter_id)
            .first()
        )
        if not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

        return ChapterWithVersionsResponse(
            id=chapter.id,
            novel_id=chapter.novel_id,
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            summary=chapter.real_summary,
            word_count=chapter.word_count,
            status=chapter.status.upper() if chapter.status else "DRAFT",
            selected_version_id=chapter.selected_version_id,
            created_at=chapter.created_at,
            updated_at=chapter.updated_at,
            versions=[ChapterVersionResponse.model_validate(v) for v in chapter.versions],
            selected_version=ChapterVersionResponse.model_validate(chapter.selected_version) if chapter.selected_version else None,
            evaluations=[ChapterEvaluationResponse.model_validate(e) for e in chapter.evaluations],
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_chapter_with_versions: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


# ============= Chapter Evaluation =============

@router.post("/evaluations/", response_model=ChapterEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(payload: ChapterEvaluationCreate, db: Session = Depends(get_db)):
    """创建章节评估"""
    try:
        logger.info(f"Creating evaluation for chapter {payload.chapter_id}")

        # 验证章节存在
        chapter = db.query(Chapter).filter(Chapter.id == payload.chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

        # 如果指定了版本，验证版本存在
        if payload.version_id:
            version = db.query(ChapterVersion).filter(
                ChapterVersion.id == payload.version_id,
                ChapterVersion.chapter_id == payload.chapter_id
            ).first()
            if not version:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

        # 创建评估
        evaluation = ChapterEvaluation(
            chapter_id=payload.chapter_id,
            version_id=payload.version_id,
            decision=payload.decision,
            feedback=payload.feedback,
            score=payload.score,
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        logger.info(f"Evaluation created successfully: {evaluation.id}")
        return evaluation
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_evaluation: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/evaluations/chapter/{chapter_id}", response_model=List[ChapterEvaluationResponse])
async def list_evaluations(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节的所有评估"""
    try:
        logger.info(f"Fetching evaluations for chapter {chapter_id}")
        evaluations = (
            db.query(ChapterEvaluation)
            .filter(ChapterEvaluation.chapter_id == chapter_id)
            .order_by(ChapterEvaluation.created_at.desc())
            .all()
        )
        logger.info(f"Retrieved {len(evaluations)} evaluations")
        return evaluations
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_evaluations: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
