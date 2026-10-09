from concurrent.futures import ThreadPoolExecutor

from app.core import constants
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging_config import logger


class WorkerManager:
    """Runs translation jobs in background threads with progress tracking.

    A fresh DB session is used per job. Progress is tracked in memory (for
    fast polling) and persisted in the DB (for resume after interruption).
    """

    def __init__(self, max_workers: int = None):
        self._pool = ThreadPoolExecutor(
            max_workers=max_workers or settings.JOBS_MAX_WORKERS,
            thread_name_prefix="linguaflow",
        )
        self._progress = {}
        self._futures = {}

    def _set(self, task_id: str, **fields) -> None:
        state = self._progress.setdefault(task_id, {})
        state.update(fields)

    def progress_of(self, task_id: str) -> dict:
        return self._progress.get(task_id, {
            "status": constants.TASK_PENDING,
            "done": 0, "total": 0, "message": "En attente",
        })

    def is_running(self, task_id: str) -> bool:
        future = self._futures.get(task_id)
        return future is not None and not future.done()

    def submit(self, task_id: str, resume: bool = False) -> None:
        if self.is_running(task_id):
            return
        self._set(task_id, status=constants.TASK_IN_PROGRESS, done=0, total=0,
                  message="Démarrage…")
        self._futures[task_id] = self._pool.submit(self._run, task_id, resume)

    def _run(self, task_id: str, resume: bool) -> None:
        from app.services.translation_service import TranslationPipeline
        db = SessionLocal()
        try:
            def on_progress(done, total, message):
                self._set(task_id, done=done, total=total, message=message,
                          status=constants.TASK_IN_PROGRESS)

            pipeline = TranslationPipeline(db, progress=on_progress, resume=resume)
            result = pipeline.run(task_id)
            self._set(task_id, status=constants.TASK_COMPLETED,
                      done=result.get("segments", 0),
                      total=result.get("segments", 0),
                      message="Terminé", result=result)
        except Exception as exc:
            logger.exception("Tâche %s échouée", task_id)
            self._set(task_id, status=constants.TASK_FAILED, message=str(exc))
        finally:
            db.close()


worker_manager = WorkerManager()
