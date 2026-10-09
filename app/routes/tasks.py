from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core import constants
from app.core.database import get_db
from app.core.security import is_within
from app.core.config import settings
from app.schemas.task import ProgressOut, TaskOut
from app.services.task_service import TaskService
from app.workers.manager import worker_manager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
async def list_tasks(limit: int = 100, db: Session = Depends(get_db)):
    service = TaskService(db)
    return [TaskOut(**t.to_dict()).dict() for t in service.list(limit)]


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    task = TaskService(db).get(task_id)
    if not task:
        raise HTTPException(404, "Tâche inconnue.")
    return TaskOut(**task.to_dict())


@router.get("/{task_id}/progress", response_model=ProgressOut)
async def progress(task_id: str, db: Session = Depends(get_db)):
    task = TaskService(db).get(task_id)
    if not task:
        raise HTTPException(404, "Tâche inconnue.")
    live = worker_manager.progress_of(task_id)
    total = live.get("total") or task.segments_total or 0
    done = live.get("done") or task.segments_processed or 0
    percent = round(done / total * 100, 1) if total else 0.0
    return ProgressOut(
        task_id=task_id,
        status=task.status,
        done=done,
        total=total,
        message=live.get("message", ""),
        percent=percent,
    )


@router.get("/{task_id}/preview")
async def preview(task_id: str, limit: int = 50, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise HTTPException(404, "Tâche inconnue.")
    from app.models.segment import TaskSegment
    rows = (db.query(TaskSegment).filter_by(task_id=task_id)
            .order_by(TaskSegment.segment_index).limit(limit).all())
    return {
        "task_id": task_id,
        "segments": [
            {"index": r.segment_index, "source": r.source_text,
             "translated": r.corrected_text or r.translated_text,
             "status": r.status}
            for r in rows
        ],
    }


@router.post("/{task_id}/resume")
async def resume(task_id: str, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise HTTPException(404, "Tâche inconnue.")
    if task.status == constants.TASK_COMPLETED:
        return JSONResponse({"detail": "Tâche déjà terminée.", "task_id": task_id})
    if not Path(task.source_path).exists():
        raise HTTPException(
            410, "Le fichier source n'est plus disponible : reprise impossible."
        )
    service.set_status(task_id, constants.TASK_IN_PROGRESS)
    worker_manager.submit(task_id, resume=True)
    return {"task_id": task_id, "resumed": True}


@router.get("/{task_id}/download")
async def download(task_id: str, db: Session = Depends(get_db)):
    task = TaskService(db).get(task_id)
    if not task:
        raise HTTPException(404, "Tâche inconnue.")
    if not task.result_path:
        raise HTTPException(409, "Aucun résultat disponible pour cette tâche.")
    path = Path(task.result_path)
    if not is_within(settings.RESULTS_DIR, path) or not path.exists():
        raise HTTPException(404, "Résultat introuvable.")
    return FileResponse(str(path), filename=path.name,
                        media_type="application/octet-stream")


@router.delete("/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise HTTPException(404, "Tâche inconnue.")
    # Remove associated files.
    for p in [task.result_path, task.source_path]:
        if p:
            Path(p).unlink(missing_ok=True)
    service.delete(task_id)
    return {"deleted": task_id}
