import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import LinguaFlowError
from app.core.logging_config import logger
from app.core.security import (new_task_id, sanitize_filename, sha256_of_file,
                               validate_extension, validate_size, secure_temp_path)
from app.schemas.task import UploadResponse
from app.services.config_service import config_service
from app.services.formatters.registry import registry
from app.services.language_detector import detector
from app.services.task_service import TaskService
from app.workers.manager import worker_manager

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    target_lang: str = Form("fr"),
    source_lang: str = Form(""),
    engine: str = Form(""),
    correction: bool = Form(False),
    remote_consent: bool = Form(False),
    db: Session = Depends(get_db),
):
    filename = sanitize_filename(file.filename or "document")
    try:
        ext = validate_extension(filename)
    except LinguaFlowError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))

    dest = secure_temp_path(filename)
    size = 0
    async with aiofiles.open(dest, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > config_service.get("max_file_size_mb", 50) * 1024 * 1024:
                await out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "Fichier trop volumineux.")
            await out.write(chunk)

    try:
        validate_size(dest)
    except LinguaFlowError as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=exc.status_code, detail=str(exc))

    checksum = sha256_of_file(dest)
    task_id = new_task_id()
    service = TaskService(db)
    service.create(
        task_id=task_id,
        filename=filename,
        file_type=ext,
        source_path=str(dest),
        target_lang=target_lang or config_service.get("default_target_lang", "fr"),
        source_lang=source_lang or None,
        engine_mode="local",
        correction=correction,
        checksum=checksum,
    )
    if engine:
        task = service.get(task_id)
        task.engine_used = engine
        db.commit()
    if remote_consent:
        config_service.update({"remote_consent": True})

    # Lightweight extraction to report segment count / detected language.
    segments_count = 0
    detected = None
    try:
        formatter = registry.get_for_path(dest)
        extraction = formatter.extract(dest)
        segments_count = len(extraction.segments)
        service.get(task_id).segments_total = segments_count
        db.commit()
        if not source_lang and extraction.segments:
            sample = "\n".join(s.text for s in extraction.segments[:20])
            detected = detector.detect(sample)
            service.get(task_id).detected_lang = detected
            db.commit()
    except Exception as exc:
        logger.warning("Extraction préalable échouée: %s", exc)
        service.add_error(task_id, f"Extraction préalable: {exc}")

    worker_manager.submit(task_id, resume=False)

    return UploadResponse(
        task_id=task_id,
        filename=filename,
        file_type=ext,
        detected_lang=detected,
        engine_mode="local",
        segments=segments_count,
    )


@router.get("/formats")
async def formats():
    return {
        "formats": registry.supported_extensions(),
        "details": registry.describe(),
    }
