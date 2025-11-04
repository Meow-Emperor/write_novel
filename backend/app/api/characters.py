from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..models.character import Character
from ..schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("/", response_model=List[CharacterResponse])
async def list_characters(novel_id: UUID = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of characters."""
    try:
        logger.info(f"Fetching characters with novel_id={novel_id}, skip={skip}, limit={limit}")
        query = db.query(Character)
        if novel_id:
            query = query.filter(Character.novel_id == str(novel_id))
        characters = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(characters)} characters")
        return characters
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_characters: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single character by its identifier."""
    try:
        logger.info(f"Fetching character with id={character_id}")
        character = db.query(Character).filter(Character.id == str(character_id)).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_character: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not character:
        logger.warning(f"Character not found: {character_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    
    logger.info(f"Retrieved character: {character.name}")
    return character


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(payload: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character entry."""
    try:
        logger.info(f"Creating character: {payload.name}")
        character = Character(**payload.model_dump())
        db.add(character)
        db.commit()
        db.refresh(character)
        logger.info(f"Character created successfully: {character.id}")
        return character
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_character: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: UUID, payload: CharacterUpdate, db: Session = Depends(get_db)):
    """Update an existing character."""
    try:
        logger.info(f"Updating character: {character_id}")
        character = db.query(Character).filter(Character.id == str(character_id)).first()
        if not character:
            logger.warning(f"Character not found for update: {character_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

        update_data = payload.model_dump(exclude_unset=True)
        logger.debug(f"Update data: {update_data}")
        for field, value in update_data.items():
            setattr(character, field, value)

        db.commit()
        db.refresh(character)
        logger.info(f"Character updated successfully: {character_id}")
        return character
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in update_character: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: UUID, db: Session = Depends(get_db)):
    """Delete a character by identifier."""
    try:
        logger.info(f"Deleting character: {character_id}")
        character = db.query(Character).filter(Character.id == str(character_id)).first()
        if not character:
            logger.warning(f"Character not found for deletion: {character_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

        db.delete(character)
        db.commit()
        logger.info(f"Character deleted successfully: {character_id}")
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in delete_character: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
