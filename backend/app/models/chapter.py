from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

BIGINT_PK_TYPE = BigInteger().with_variant(Integer, "sqlite")
LONG_TEXT_TYPE = Text().with_variant(LONGTEXT, "mysql")


class Chapter(Base):
    """章节正文状态，指向选中的版本。"""

    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(BIGINT_PK_TYPE, primary_key=True, autoincrement=True)
    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    outline: Mapped[Optional[str]] = mapped_column(Text)
    real_summary: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="not_generated")
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    selected_version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chapter_versions.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    novel: Mapped["Novel"] = relationship(back_populates="chapters")
    versions: Mapped[list["ChapterVersion"]] = relationship(
        "ChapterVersion",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="ChapterVersion.created_at",
        primaryjoin="Chapter.id == ChapterVersion.chapter_id",
        foreign_keys="[ChapterVersion.chapter_id]",
    )
    selected_version: Mapped[Optional["ChapterVersion"]] = relationship(
        "ChapterVersion",
        foreign_keys=[selected_version_id],
        primaryjoin="Chapter.selected_version_id == ChapterVersion.id",
        post_update=True,
    )
    evaluations: Mapped[list["ChapterEvaluation"]] = relationship(
        back_populates="chapter", cascade="all, delete-orphan", order_by="ChapterEvaluation.created_at"
    )


class ChapterVersion(Base):
    """章节生成的不同版本文本。"""

    __tablename__ = "chapter_versions"

    id: Mapped[int] = mapped_column(BIGINT_PK_TYPE, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    version_label: Mapped[Optional[str]] = mapped_column(String(64))
    provider: Mapped[Optional[str]] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(LONG_TEXT_TYPE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped[Chapter] = relationship(
        "Chapter",
        back_populates="versions",
        foreign_keys=[chapter_id],
    )
    evaluations: Mapped[list["ChapterEvaluation"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )


class ChapterEvaluation(Base):
    """章节评估记录。"""

    __tablename__ = "chapter_evaluations"

    id: Mapped[int] = mapped_column(BIGINT_PK_TYPE, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    version_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chapter_versions.id", ondelete="CASCADE"))
    decision: Mapped[Optional[str]] = mapped_column(String(32))
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    score: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped[Chapter] = relationship(back_populates="evaluations")
    version: Mapped[Optional[ChapterVersion]] = relationship(back_populates="evaluations")
