from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

BIGINT_PK_TYPE = BigInteger().with_variant(Integer, "sqlite")


class WorldSetting(Base):
    __tablename__ = "world_settings"

    id: Mapped[int] = mapped_column(BIGINT_PK_TYPE, primary_key=True, autoincrement=True)
    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    era: Mapped[Optional[str]] = mapped_column(String(100))
    locations: Mapped[Optional[dict]] = mapped_column(JSON)
    rules: Mapped[Optional[dict]] = mapped_column(JSON)
    culture: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    novel: Mapped["Novel"] = relationship(back_populates="worlds")
