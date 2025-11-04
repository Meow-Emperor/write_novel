from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..models.world import WorldSetting
from ..schemas.world import WorldSettingCreate, WorldSettingResponse, WorldSettingUpdate

router = APIRouter(prefix="/api/worlds", tags=["worlds"])


@router.get("/", response_model=List[WorldSettingResponse])
async def list_world_settings(novel_id: UUID = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of world settings."""
    try:
        logger.info(f"Fetching world settings with novel_id={novel_id}, skip={skip}, limit={limit}")
        query = db.query(WorldSetting)
        if novel_id:
            query = query.filter(WorldSetting.novel_id == str(novel_id))
        world_settings = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(world_settings)} world settings")
        return world_settings
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_world_settings: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{world_id}", response_model=WorldSettingResponse)
async def get_world_setting(world_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single world setting by its identifier."""
    try:
        logger.info(f"Fetching world setting with id={world_id}")
        world_setting = db.query(WorldSetting).filter(WorldSetting.id == str(world_id)).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_world_setting: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not world_setting:
        logger.warning(f"World setting not found: {world_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World setting not found")
    
    logger.info(f"Retrieved world setting for novel: {world_setting.novel_id}")
    return world_setting


@router.get("/novel/{novel_id}", response_model=WorldSettingResponse)
async def get_world_by_novel(novel_id: UUID, db: Session = Depends(get_db)):
    """Retrieve world setting by novel ID."""
    try:
        logger.info(f"Fetching world setting for novel: {novel_id}")
        world_setting = db.query(WorldSetting).filter(WorldSetting.novel_id == str(novel_id)).first()
        
        if not world_setting:
            logger.warning(f"World setting not found for novel: {novel_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World setting not found for this novel")
        
        logger.info(f"Retrieved world setting: {world_setting.id}")
        return world_setting
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_world_by_novel: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/", response_model=WorldSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_world_setting(payload: WorldSettingCreate, db: Session = Depends(get_db)):
    """Create a new world setting entry."""
    try:
        logger.info(f"Creating world setting for novel: {payload.novel_id}")
        
        # Check if world setting already exists for this novel
        existing = db.query(WorldSetting).filter(WorldSetting.novel_id == str(payload.novel_id)).first()
        if existing:
            logger.warning(f"World setting already exists for novel: {payload.novel_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="World setting already exists for this novel"
            )
        
        world_setting = WorldSetting(**payload.model_dump())
        db.add(world_setting)
        db.commit()
        db.refresh(world_setting)
        logger.info(f"World setting created successfully: {world_setting.id}")
        return world_setting
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_world_setting: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{world_id}", response_model=WorldSettingResponse)
async def update_world_setting(world_id: UUID, payload: WorldSettingUpdate, db: Session = Depends(get_db)):
    """Update an existing world setting."""
    try:
        logger.info(f"Updating world setting: {world_id}")
        world_setting = db.query(WorldSetting).filter(WorldSetting.id == str(world_id)).first()
        if not world_setting:
            logger.warning(f"World setting not found for update: {world_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World setting not found")

        update_data = payload.model_dump(exclude_unset=True)
        logger.debug(f"Update data: {update_data}")
        for field, value in update_data.items():
            setattr(world_setting, field, value)

        db.commit()
        db.refresh(world_setting)
        logger.info(f"World setting updated successfully: {world_id}")
        return world_setting
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in update_world_setting: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{world_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_world_setting(world_id: UUID, db: Session = Depends(get_db)):
    """Delete a world setting by identifier."""
    try:
        logger.info(f"Deleting world setting: {world_id}")
        world_setting = db.query(WorldSetting).filter(WorldSetting.id == str(world_id)).first()
        if not world_setting:
            logger.warning(f"World setting not found for deletion: {world_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World setting not found")

        db.delete(world_setting)
        db.commit()
        logger.info(f"World setting deleted successfully: {world_id}")
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in delete_world_setting: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
