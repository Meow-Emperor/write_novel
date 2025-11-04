from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..core.database import Base


class WorldSetting(Base):
    __tablename__ = "world_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    novel_id = Column(String(36), ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, unique=True)
    era = Column(String(100))
    locations = Column(JSON)
    rules = Column(JSON)
    culture = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    novel = relationship("Novel", back_populates="world_setting")
