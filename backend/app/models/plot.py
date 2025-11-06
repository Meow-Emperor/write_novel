from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

BIGINT_PK_TYPE = BigInteger().with_variant(Integer, "sqlite")


class Plot(Base):
    __tablename__ = "plots"

    id: Mapped[int] = mapped_column(BIGINT_PK_TYPE, primary_key=True, autoincrement=True)
    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    act: Mapped[Optional[str]] = mapped_column(String(50))
    key_events: Mapped[Optional[str]] = mapped_column(Text)
    characters: Mapped[Optional[str]] = mapped_column(Text)
    conflicts: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    novel: Mapped["Novel"] = relationship(back_populates="plots")
