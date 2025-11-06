from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..models.character import Character
from ..schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("/", response_model=List[CharacterResponse])
@router.get("", response_model=List[CharacterResponse])
async def list_characters(novel_id: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of characters."""
    try:
        logger.info(f"Fetching characters with novel_id={novel_id}, skip={skip}, limit={limit}")
        query = db.query(Character)
        if novel_id:
            query = query.filter(Character.novel_id == str(novel_id))
        characters = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(characters)} characters")
        # Build response objects to maintain schema compatibility
        return [
            CharacterResponse(
                id=c.id,
                novel_id=c.novel_id,
                name=c.name,
                role=c.identity,
                description=(c.extra or {}).get("description") if isinstance(c.extra, dict) else None,
                personality=c.personality,
                background=c.background,
                appearance=c.appearance,
                relationships=c.relationship_to_protagonist,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in characters
        ]
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_characters: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: int, db: Session = Depends(get_db)):
    """Retrieve a single character by its identifier."""
    try:
        logger.info(f"Fetching character with id={character_id}")
        character = db.query(Character).filter(Character.id == character_id).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_character: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not character:
        logger.warning(f"Character not found: {character_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    
    logger.info(f"Retrieved character: {character.name}")
    return CharacterResponse(
        id=character.id,
        novel_id=character.novel_id,
        name=character.name,
        role=character.identity,
        description=(character.extra or {}).get("description") if isinstance(character.extra, dict) else None,
        personality=character.personality,
        background=character.background,
        appearance=character.appearance,
        relationships=character.relationship_to_protagonist,
        created_at=character.created_at,
        updated_at=character.updated_at,
    )


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(payload: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character entry."""
    try:
        logger.info(f"Creating character: {payload.name}")
        # Map schema fields to model columns and preserve extra info
        data = payload.model_dump()
        character = Character(
            novel_id=str(data.get('novel_id')),
            name=data.get('name'),
            identity=data.get('role'),
            personality=data.get('personality'),
            background=data.get('background'),
            appearance=data.get('appearance'),
            relationship_to_protagonist=data.get('relationships'),
            extra={"description": data.get('description')} if data.get('description') else None,
        )
        db.add(character)
        db.commit()
        db.refresh(character)
        logger.info(f"Character created successfully: {character.id}")
        return CharacterResponse(
            id=character.id,
            novel_id=character.novel_id,
            name=character.name,
            role=character.identity,
            description=(character.extra or {}).get("description") if isinstance(character.extra, dict) else None,
            personality=character.personality,
            background=character.background,
            appearance=character.appearance,
            relationships=character.relationship_to_protagonist,
            created_at=character.created_at,
            updated_at=character.updated_at,
        )
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_character: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: int, payload: CharacterUpdate, db: Session = Depends(get_db)):
    """Update an existing character."""
    try:
        logger.info(f"Updating character: {character_id}")
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            logger.warning(f"Character not found for update: {character_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

        update_data = payload.model_dump(exclude_unset=True)
        logger.debug(f"Update data: {update_data}")
        # Map update fields explicitly
        if 'name' in update_data:
            character.name = update_data['name']
        if 'role' in update_data:
            character.identity = update_data['role']
        if 'personality' in update_data:
            character.personality = update_data['personality']
        if 'background' in update_data:
            character.background = update_data['background']
        if 'appearance' in update_data:
            character.appearance = update_data['appearance']
        if 'relationships' in update_data:
            character.relationship_to_protagonist = update_data['relationships']
        if 'description' in update_data:
            existing_extra = character.extra if isinstance(character.extra, dict) else {}
            existing_extra.update({"description": update_data['description']})
            character.extra = existing_extra

        db.commit()
        db.refresh(character)
        logger.info(f"Character updated successfully: {character_id}")
        return CharacterResponse(
            id=character.id,
            novel_id=character.novel_id,
            name=character.name,
            role=character.identity,
            description=(character.extra or {}).get("description") if isinstance(character.extra, dict) else None,
            personality=character.personality,
            background=character.background,
            appearance=character.appearance,
            relationships=character.relationship_to_protagonist,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in update_character: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Delete a character by identifier."""
    try:
        logger.info(f"Deleting character: {character_id}")
        character = db.query(Character).filter(Character.id == character_id).first()
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
