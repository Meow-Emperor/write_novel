from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Plot(Base):
    __tablename__ = "plots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    novel_id = Column(String(36), ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    act = Column(String(50))
    key_events = Column(Text)
    characters = Column(Text)
    conflicts = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    novel = relationship("Novel", back_populates="plots")

    def __repr__(self) -> str:
        return f"<Plot id={self.id} title={self.title!r}>"
