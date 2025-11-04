"""
小说管理API路由
提供小说的增删改查(CRUD)接口
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.novel import Novel
from ..schemas.novel import NovelCreate, NovelResponse, NovelUpdate

# 创建小说路由器，前缀为/api/novels
router = APIRouter(prefix="/api/novels", tags=["novels"])


@router.get("/", response_model=List[NovelResponse])
async def list_novels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取小说列表（分页）
    
    Args:
        skip: 跳过的记录数（用于分页）
        limit: 返回的最大记录数
        db: 数据库会话（依赖注入）
        
    Returns:
        小说列表
    """
    try:
        novels = db.query(Novel).offset(skip).limit(limit).all()
        return novels
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: UUID, db: Session = Depends(get_db)):
    """
    根据ID获取单个小说详情
    
    Args:
        novel_id: 小说UUID
        db: 数据库会话（依赖注入）
        
    Returns:
        小说详情
        
    Raises:
        404: 小说不存在
    """
    try:
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    return novel


@router.post("/", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def create_novel(payload: NovelCreate, db: Session = Depends(get_db)):
    """
    创建新小说
    
    Args:
        payload: 小说创建数据
        db: 数据库会话（依赖注入）
        
    Returns:
        创建的小说信息
    """
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
    """
    更新现有小说
    
    Args:
        novel_id: 小说UUID
        payload: 更新数据（仅更新提供的字段）
        db: 数据库会话（依赖注入）
        
    Returns:
        更新后的小说信息
        
    Raises:
        404: 小说不存在
    """
    try:
        novel = db.query(Novel).filter(Novel.id == str(novel_id)).first()
        if not novel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

        # 只更新提供的字段
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
    """
    删除小说
    
    Args:
        novel_id: 小说UUID
        db: 数据库会话（依赖注入）
        
    Raises:
        404: 小说不存在
    """
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
