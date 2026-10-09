from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from app.models._time import utcnow

from app.models.base import Base


class TranslationTask(Base):
    __tablename__ = "translation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    source_lang = Column(String)
    detected_lang = Column(String)
    target_lang = Column(String, default="fr")
    engine_used = Column(String)
    engine_mode = Column(String, default="local")
    status = Column(String, default="pending", index=True)
    segments_total = Column(Integer, default=0)
    segments_processed = Column(Integer, default=0)
    errors = Column(Text)
    warnings = Column(Text)
    result_path = Column(String)
    source_path = Column(String)
    source_checksum = Column(String)
    correction_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    completed_at = Column(DateTime)

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "source_lang": self.source_lang,
            "detected_lang": self.detected_lang,
            "target_lang": self.target_lang,
            "engine_used": self.engine_used,
            "engine_mode": self.engine_mode,
            "status": self.status,
            "segments_total": self.segments_total,
            "segments_processed": self.segments_processed,
            "errors": self.errors,
            "warnings": self.warnings,
            "result_path": self.result_path,
            "correction_enabled": self.correction_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
