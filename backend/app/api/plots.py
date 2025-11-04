from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logger import logger
from ..models.plot import Plot
from ..schemas.plot import PlotCreate, PlotResponse, PlotUpdate

router = APIRouter(prefix="/api/plots", tags=["plots"])


@router.get("/", response_model=List[PlotResponse])
async def list_plots(novel_id: UUID = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of plots."""
    try:
        logger.info(f"Fetching plots with novel_id={novel_id}, skip={skip}, limit={limit}")
        query = db.query(Plot)
        if novel_id:
            query = query.filter(Plot.novel_id == str(novel_id))
        plots = query.order_by(Plot.order).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(plots)} plots")
        return plots
    except SQLAlchemyError as exc:
        logger.error(f"Database error in list_plots: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/{plot_id}", response_model=PlotResponse)
async def get_plot(plot_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single plot by its identifier."""
    try:
        logger.info(f"Fetching plot with id={plot_id}")
        plot = db.query(Plot).filter(Plot.id == str(plot_id)).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error in get_plot: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not plot:
        logger.warning(f"Plot not found: {plot_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")
    
    logger.info(f"Retrieved plot: {plot.title}")
    return plot


@router.post("/", response_model=PlotResponse, status_code=status.HTTP_201_CREATED)
async def create_plot(payload: PlotCreate, db: Session = Depends(get_db)):
    """Create a new plot entry."""
    try:
        logger.info(f"Creating plot: {payload.title}")
        plot = Plot(**payload.model_dump())
        db.add(plot)
        db.commit()
        db.refresh(plot)
        logger.info(f"Plot created successfully: {plot.id}")
        return plot
    except SQLAlchemyError as exc:
        logger.error(f"Database error in create_plot: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.put("/{plot_id}", response_model=PlotResponse)
async def update_plot(plot_id: UUID, payload: PlotUpdate, db: Session = Depends(get_db)):
    """Update an existing plot."""
    try:
        logger.info(f"Updating plot: {plot_id}")
        plot = db.query(Plot).filter(Plot.id == str(plot_id)).first()
        if not plot:
            logger.warning(f"Plot not found for update: {plot_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        update_data = payload.model_dump(exclude_unset=True)
        logger.debug(f"Update data: {update_data}")
        for field, value in update_data.items():
            setattr(plot, field, value)

        db.commit()
        db.refresh(plot)
        logger.info(f"Plot updated successfully: {plot_id}")
        return plot
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in update_plot: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plot(plot_id: UUID, db: Session = Depends(get_db)):
    """Delete a plot by identifier."""
    try:
        logger.info(f"Deleting plot: {plot_id}")
        plot = db.query(Plot).filter(Plot.id == str(plot_id)).first()
        if not plot:
            logger.warning(f"Plot not found for deletion: {plot_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        db.delete(plot)
        db.commit()
        logger.info(f"Plot deleted successfully: {plot_id}")
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error(f"Database error in delete_plot: {exc}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
