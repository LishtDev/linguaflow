from app.models._time import utcnow
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core import constants
from app.core.logging_config import logger
from app.models.segment import TaskSegment
from app.models.task import TranslationTask


class TaskService:
    """Persistence for translation jobs, segments and resume support."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, task_id: str, filename: str, file_type: str,
               source_path: str, target_lang: str, source_lang: Optional[str],
               engine_mode: str = "local", correction: bool = False,
               checksum: str = "") -> TranslationTask:
        task = TranslationTask(
            task_id=task_id,
            filename=filename,
            file_type=file_type,
            target_lang=target_lang,
            source_lang=source_lang,
            source_path=source_path,
            engine_mode=engine_mode,
            correction_enabled=correction,
            source_checksum=checksum,
            status=constants.TASK_PENDING,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get(self, task_id: str) -> Optional[TranslationTask]:
        return self.db.query(TranslationTask).filter_by(task_id=task_id).first()

    def list(self, limit: int = 100) -> List[TranslationTask]:
        return (self.db.query(TranslationTask)
                .order_by(TranslationTask.created_at.desc())
                .limit(limit).all())

    def set_status(self, task_id: str, status: str, **fields) -> None:
        task = self.get(task_id)
        if not task:
            return
        task.status = status
        for k, v in fields.items():
            if hasattr(task, k):
                setattr(task, k, v)
        if status in (constants.TASK_COMPLETED, constants.TASK_FAILED):
            task.completed_at = utcnow()
        self.db.commit()

    def update_progress(self, task_id: str, processed: int, total: int) -> None:
        task = self.get(task_id)
        if not task:
            return
        task.segments_processed = processed
        task.segments_total = total
        self.db.commit()

    def add_error(self, task_id: str, message: str) -> None:
        task = self.get(task_id)
        if not task:
            return
        existing = task.errors or ""
        task.errors = (existing + "\n" + message).strip()
        self.db.commit()

    def set_warnings(self, task_id: str, warnings: List[str]) -> None:
        task = self.get(task_id)
        if not task:
            return
        task.warnings = "\n".join(warnings)
        self.db.commit()

    # --- Segments (for resume) -------------------------------------------
    def save_segments(self, task_id: str, segments) -> None:
        self.db.query(TaskSegment).filter_by(task_id=task_id).delete()
        for seg in segments:
            self.db.add(TaskSegment(
                task_id=task_id,
                segment_index=seg if isinstance(seg, int) else seg.index,
                status="pending",
            ))
        self.db.commit()

    def ensure_segment(self, task_id: str, index: int, source_text: str) -> TaskSegment:
        seg = (self.db.query(TaskSegment)
               .filter_by(task_id=task_id, segment_index=index).first())
        if not seg:
            seg = TaskSegment(task_id=task_id, segment_index=index,
                              source_text=source_text, status="pending")
            self.db.add(seg)
            self.db.commit()
        return seg

    def save_translation(self, task_id: str, index: int, translated: str,
                         corrected: Optional[str] = None,
                         source_text: Optional[str] = None) -> None:
        seg = (self.db.query(TaskSegment)
               .filter_by(task_id=task_id, segment_index=index).first())
        if not seg:
            seg = TaskSegment(task_id=task_id, segment_index=index)
            self.db.add(seg)
        if source_text is not None:
            seg.source_text = source_text
        seg.translated_text = translated
        seg.corrected_text = corrected
        seg.status = "done"
        self.db.commit()

    def load_translations(self, task_id: str) -> Dict[int, str]:
        rows = self.db.query(TaskSegment).filter_by(task_id=task_id).all()
        result = {}
        for r in rows:
            if r.status == "done":
                result[r.segment_index] = r.corrected_text or r.translated_text
        return result

    def delete(self, task_id: str) -> None:
        self.db.query(TaskSegment).filter_by(task_id=task_id).delete()
        task = self.get(task_id)
        if task:
            self.db.delete(task)
        self.db.commit()

    def mark_interrupted(self) -> None:
        """On startup, flag tasks left in progress as resumable."""
        rows = (self.db.query(TranslationTask)
                .filter(TranslationTask.status.in_(
                    [constants.TASK_IN_PROGRESS, constants.TASK_PENDING]))
                .all())
        for row in rows:
            row.status = constants.TASK_INTERRUPTED
        if rows:
            self.db.commit()
            logger.info("%d tâche(s) marquée(s) comme interrompue(s).", len(rows))
