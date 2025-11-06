from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

BIGINT_PK_TYPE = BigInteger().with_variant(Integer, "sqlite")


class Character(Base):
    """蓝图角色信息。"""

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(BIGINT_PK_TYPE, primary_key=True, autoincrement=True)
    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    identity: Mapped[Optional[str]] = mapped_column(String(255))
    personality: Mapped[Optional[str]] = mapped_column(Text)
    goals: Mapped[Optional[str]] = mapped_column(Text)
    abilities: Mapped[Optional[str]] = mapped_column(Text)
    relationship_to_protagonist: Mapped[Optional[str]] = mapped_column(Text)
    appearance: Mapped[Optional[str]] = mapped_column(Text)
    background: Mapped[Optional[str]] = mapped_column(Text)
    extra: Mapped[Optional[dict]] = mapped_column(JSON)
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    novel: Mapped["Novel"] = relationship(back_populates="characters")
