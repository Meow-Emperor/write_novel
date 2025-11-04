from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    novel_id = Column(String(36), ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50))  # protagonist, antagonist, supporting, etc.
    description = Column(Text)
    personality = Column(Text)
    background = Column(Text)
    appearance = Column(Text)
    relationships = Column(Text)  # JSON string of relationships with other characters
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    novel = relationship("Novel", back_populates="characters")

    def __repr__(self) -> str:
        return f"<Character id={self.id} name={self.name!r}>"
