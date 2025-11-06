from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..core.security import create_access_token, hash_password, verify_password
from ..models.admin import Admin
from ..models.novel import Novel
from ..schemas.novel import NovelResponse
from ..schemas.admin import AdminCreate, AdminLogin, AdminResponse, AdminUpdate, Token

router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Admin:
    """Get the current authenticated admin."""
    from ..core.security import decode_access_token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive admin account",
        )
    
    return admin


async def get_current_superuser(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """Require superuser privileges."""
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges",
        )
    return current_admin


@router.post("/login", response_model=Token)
async def login(payload: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint."""
    try:
        logger.info(f"Admin login attempt: {payload.username}")
        admin = db.query(Admin).filter(Admin.username == payload.username).first()
        
        if not admin or not verify_password(payload.password, admin.hashed_password):
            logger.warning(f"Failed login attempt for: {payload.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        
        if not admin.is_active:
            logger.warning(f"Inactive admin login attempt: {payload.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive",
            )
        
        admin.last_login = datetime.utcnow()
        db.commit()
        
        access_token = create_access_token(
            subject=admin.id,
            expires_delta=timedelta(hours=24)
        )
        
        logger.info(f"Admin logged in successfully: {payload.username}")
        return Token(access_token=access_token)
    
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in login: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        ) from exc


@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(
    payload: AdminCreate,
    db: Session = Depends(get_db)
):
    """Register a new admin (first admin can self-register, others need superuser)."""
    try:
        admin_count = db.query(Admin).count()

        # First admin can self-register, others would need authentication
        # For simplicity, we allow registration if no admins exist
        if admin_count > 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin registration is closed. Contact existing superuser.",
            )
        
        existing_admin = db.query(Admin).filter(
            (Admin.username == payload.username) | (Admin.email == payload.email)
        ).first()
        
        if existing_admin:
            logger.warning(f"Admin registration failed: username or email already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )
        
        admin_data = payload.model_dump(exclude={"password", "is_superuser"})
        admin = Admin(
            **admin_data,
            hashed_password=hash_password(payload.password),
            is_superuser=True if admin_count == 0 else payload.is_superuser
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        logger.info(f"Admin registered successfully: {admin.username}")
        return admin
    
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in register_admin: {exc}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/can-register")
async def can_register(db: Session = Depends(get_db)):
    """Public endpoint: whether registration is allowed (no admins yet)."""
    try:
        admin_count = db.query(Admin).count()
        return {"can_register": admin_count == 0}
    except SQLAlchemyError as exc:
        logger.error(f"Database error in can_register: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        ) from exc


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    """Get current admin information."""
    return current_admin


@router.get("/admins", response_model=List[AdminResponse])
async def list_admins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_superuser)
):
    """List all admins (superuser only)."""
    try:
        logger.info(f"Fetching admins with skip={skip}, limit={limit}")
        admins = db.query(Admin).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(admins)} admins")
        return admins
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_admins: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.put("/admins/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: UUID,
    payload: AdminUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update an admin (self or superuser only)."""
    try:
        admin = db.query(Admin).filter(Admin.id == str(admin_id)).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found",
            )
        
        if admin.id != current_admin.id and not current_admin.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough privileges",
            )
        
        update_data = payload.model_dump(exclude_unset=True, exclude={"password"})
        
        for field, value in update_data.items():
            if field == "is_superuser" and not current_admin.is_superuser:
                continue
            setattr(admin, field, value)
        
        if payload.password:
            admin.hashed_password = hash_password(payload.password)
        
        db.commit()
        db.refresh(admin)
        
        logger.info(f"Admin updated successfully: {admin_id}")
        return admin
    
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in update_admin: {exc}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.delete("/admins/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(
    admin_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_superuser)
):
    """Delete an admin (superuser only)."""
    try:
        if str(admin_id) == current_admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account",
            )
        
        admin = db.query(Admin).filter(Admin.id == str(admin_id)).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found",
            )
        
        db.delete(admin)
        db.commit()
        
        logger.info(f"Admin deleted successfully: {admin_id}")
    
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in delete_admin: {exc}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin)
):
    """Get platform statistics."""
    try:
        novel_count = db.query(Novel).count()
        # Normalize to lowercase statuses used by the model (default 'draft')
        draft_count = db.query(Novel).filter(Novel.status.in_(["draft", "DRAFT"])) .count()
        in_progress_count = db.query(Novel).filter(Novel.status.in_(["in_progress", "IN_PROGRESS"])) .count()
        completed_count = db.query(Novel).filter(Novel.status.in_(["completed", "COMPLETED"])) .count()
        published_count = db.query(Novel).filter(Novel.status.in_(["published", "PUBLISHED"])) .count()
        admin_count = db.query(Admin).count()
        
        return {
            "novels": {
                "total": novel_count,
                "draft": draft_count,
                "in_progress": in_progress_count,
                "completed": completed_count,
                "published": published_count,
            },
            "admins": admin_count,
        }
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_stats: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/novels", response_model=List[NovelResponse])
async def admin_list_novels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin)
):
    """List all novels (admin view with more details)."""
    try:
        logger.info(f"Admin fetching novels with skip={skip}, limit={limit}")
        from .novels import _build_response
        novels = db.query(Novel).order_by(Novel.created_at.desc()).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(novels)} novels for admin")
        return [_build_response(n) for n in novels]
    except SQLAlchemyError as exc:
        logger.error(f"Database error in admin_list_novels: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
