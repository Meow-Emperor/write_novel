from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class NovelStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PUBLISHED = "PUBLISHED"


class Novel(Base):
    __tablename__ = "novels"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    author = Column(String(100))
    genre = Column(String(50))
    description = Column("synopsis", Text)
    status = Column(SQLEnum(NovelStatus, native_enum=False), default=NovelStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    world_setting = relationship("WorldSetting", back_populates="novel", uselist=False, cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="novel", cascade="all, delete-orphan")
    plots = relationship("Plot", back_populates="novel", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Novel id={self.id} title={self.title!r}>"

    @property
    def synopsis(self) -> str | None:
        return self.description

    @synopsis.setter
    def synopsis(self, value: str | None) -> None:
        self.description = value
