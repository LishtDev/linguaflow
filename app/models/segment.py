from sqlalchemy import Column, Integer, String, Text, DateTime
from app.models._time import utcnow

from app.models.base import Base


class TaskSegment(Base):
    """Intermediate translation results, enabling resume after interruption."""
    __tablename__ = "task_segments"

    id = Column(Integer, primary_key=True)
    task_id = Column(String, index=True, nullable=False)
    segment_index = Column(Integer, nullable=False)
    source_text = Column(Text)
    translated_text = Column(Text)
    corrected_text = Column(Text)
    status = Column(String, default="pending")  # pending | done | error
    error = Column(Text)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
