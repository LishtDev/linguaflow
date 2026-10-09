import hashlib
from pathlib import Path

import pytest

from app.core.exceptions import ExtractionError
from app.core.security import new_task_id
from app.services.task_service import TaskService
from app.services.translation_service import TranslationPipeline


def test_ocr_unavailable_raises_clear_error(monkeypatch):
    from app.services.ocr import ocr_service as mod
    monkeypatch.setattr(mod, "_OCR_AVAILABLE", False)
    svc = mod.OcrService()
    assert svc.is_available() is False
    with pytest.raises(ExtractionError):
        svc.extract_text(Path("/tmp/does-not-matter.png"))


def test_image_formatter_reports_ocr_requirement(db, tmp_path, monkeypatch):
    from app.services.ocr import ocr_service as mod
    monkeypatch.setattr(mod, "_OCR_AVAILABLE", False)
    f = tmp_path / "scan.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\n")  # not a real image
    task_id = new_task_id()
    TaskService(db).create(task_id=task_id, filename="scan.png", file_type="png",
                           source_path=str(f), target_lang="fr", source_lang="en")
    with pytest.raises(Exception):
        TranslationPipeline(db).run(task_id)


def test_local_pipeline_makes_no_network_calls(db, tmp_path, mock_engine, monkeypatch):
    """In local mode, translating must never perform external HTTP requests."""
    import httpx

    called = {"n": 0}

    def guard(*args, **kwargs):
        called["n"] += 1
        raise AssertionError("A network call was attempted in local mode!")

    monkeypatch.setattr(httpx, "Client", guard)
    monkeypatch.setattr(httpx, "get", guard)
    monkeypatch.setattr(httpx, "post", guard)

    f = tmp_path / "n.txt"
    f.write_text("Hello world\n", encoding="utf-8")
    task_id = new_task_id()
    TaskService(db).create(task_id=task_id, filename="n.txt", file_type="txt",
                           source_path=str(f), target_lang="fr", source_lang="en",
                           checksum=hashlib.sha256(f.read_bytes()).hexdigest())
    result = TranslationPipeline(db).run(task_id)
    assert result["status"] == "completed"
    assert called["n"] == 0


def test_remote_engine_never_called_without_consent(db, tmp_path, monkeypatch):
    """A remote engine must be refused when the user has not consented."""
    from app.core.exceptions import RemoteEngineDisabledError
    from app.services.config_service import config_service

    monkeypatch.setattr(config_service, "_cache", {
        **config_service.all(),
        "remote_enabled": True,
        "remote_endpoint": "http://127.0.0.1:5000",
        "remote_consent": False,
    })

    f = tmp_path / "r.txt"
    f.write_text("Hello world\n", encoding="utf-8")
    task_id = new_task_id()
    TaskService(db).create(task_id=task_id, filename="r.txt", file_type="txt",
                           source_path=str(f), target_lang="fr", source_lang="en",
                           checksum=hashlib.sha256(f.read_bytes()).hexdigest())
    task = TaskService(db).get(task_id)
    task.engine_used = "libretranslate"  # explicit remote request
    db.commit()

    with pytest.raises(RemoteEngineDisabledError):
        TranslationPipeline(db).run(task_id)
