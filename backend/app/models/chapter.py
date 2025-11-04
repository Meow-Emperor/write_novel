from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    novel_id = Column(String(36), ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    word_count = Column(Integer, default=0)
    status = Column(String(50), default="draft")  # draft, in_progress, completed, published
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    novel = relationship("Novel", back_populates="chapters")

    def __repr__(self) -> str:
        return f"<Chapter id={self.id} title={self.title!r} number={self.chapter_number}>"
