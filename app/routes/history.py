from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def list_history(limit: int = 100, db: Session = Depends(get_db)):
    return [t.to_dict() for t in TaskService(db).list(limit)]


@router.delete("")
async def clear_history(db: Session = Depends(get_db)):
    """Delete all history entries and their associated files.

    Source uploads live in the temp directory and results in results/, both are
    cleared to honor the user's right to erase their data.
    """
    service = TaskService(db)
    count = 0
    for task in service.list(limit=100000):
        for p in [task.result_path, task.source_path]:
            if p:
                try:
                    Path(p).unlink(missing_ok=True)
                except Exception:
                    pass
        service.delete(task.task_id)
        count += 1
    return {"deleted": count}
