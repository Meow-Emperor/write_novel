from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

# 自定义列类型：兼容跨数据库环境
BIGINT_PK_TYPE = BigInteger().with_variant(Integer, "sqlite")
LONG_TEXT_TYPE = Text().with_variant(LONGTEXT, "mysql")


class _MetadataAccessor:
    """Descriptor 用于将 `metadata` 访问重定向到 `metadata_`，且保持 Base.metadata 可用。"""

    def __get__(self, instance, owner):
        if instance is None:
            return Base.metadata
        return instance.metadata_

    def __set__(self, instance, value):
        instance.metadata_ = value


class Novel(Base):
    """小说项目主表，仅存放轻量级元数据。"""

    __tablename__ = "novels"

    # 生成字符串 UUID 作为主键，避免手动传入
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    initial_prompt: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship("User", back_populates="novels")
    blueprint: Mapped[Optional["NovelBlueprint"]] = relationship(
        back_populates="novel", cascade="all, delete-orphan", uselist=False
    )
    conversations: Mapped[list["NovelConversation"]] = relationship(
        back_populates="novel", cascade="all, delete-orphan", order_by="NovelConversation.seq"
    )
    characters: Mapped[list["Character"]] = relationship(
        back_populates="novel", cascade="all, delete-orphan", order_by="Character.position"
    )
    relationships_: Mapped[list["CharacterRelationship"]] = relationship(
        back_populates="novel", cascade="all, delete-orphan", order_by="CharacterRelationship.position"
    )
    plots: Mapped[list["Plot"]] = relationship(
        back_populates="novel", cascade="all, delete-orphan"
    )
    chapters: Mapped[list["Chapter"]] = relationship(
        back_populates="novel", cascade="all, delete-orphan", order_by="Chapter.chapter_number"
    )
    worlds: Mapped[list["WorldSetting"]] = relationship(
        back_populates="novel", cascade="all, delete-orphan"
    )


class NovelConversation(Base):
    """对话记录表，存储概念阶段的连续对话。"""

    __tablename__ = "novel_conversations"

    id: Mapped[int] = mapped_column(BIGINT_PK_TYPE, primary_key=True, autoincrement=True)
    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(LONG_TEXT_TYPE, nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)
    metadata = _MetadataAccessor()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    novel: Mapped[Novel] = relationship(back_populates="conversations")


class NovelBlueprint(Base):
    """蓝图主体信息（标题、风格等）。"""

    __tablename__ = "novel_blueprints"

    novel_id: Mapped[str] = mapped_column(
        ForeignKey("novels.id", ondelete="CASCADE"), primary_key=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(255))
    target_audience: Mapped[Optional[str]] = mapped_column(String(255))
    genre: Mapped[Optional[str]] = mapped_column(String(128))
    style: Mapped[Optional[str]] = mapped_column(String(128))
    tone: Mapped[Optional[str]] = mapped_column(String(128))
    one_sentence_summary: Mapped[Optional[str]] = mapped_column(Text)
    full_synopsis: Mapped[Optional[str]] = mapped_column(LONG_TEXT_TYPE)
    world_setting: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    novel: Mapped[Novel] = relationship(back_populates="blueprint")


class CharacterRelationship(Base):
    """角色之间的关系。"""

    __tablename__ = "character_relationships"

    id: Mapped[int] = mapped_column(BIGINT_PK_TYPE, primary_key=True, autoincrement=True)
    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    character_from: Mapped[str] = mapped_column(String(255), nullable=False)
    character_to: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, default=0)

    novel: Mapped[Novel] = relationship(back_populates="relationships_")
