import hashlib
from pathlib import Path

from app.models.segment import TaskSegment
from app.services.task_service import TaskService
from app.services.translation_service import TranslationPipeline
from app.core.security import new_task_id
from app.core import constants


def _create(db, tmp_path, content):
    src = tmp_path / "resume.txt"
    src.write_text(content, encoding="utf-8")
    task_id = new_task_id()
    TaskService(db).create(task_id=task_id, filename="resume.txt", file_type="txt",
                           source_path=str(src), target_lang="fr", source_lang="en",
                           checksum=hashlib.sha256(content.encode()).hexdigest())
    return task_id, src


def test_resume_skips_completed_segments(db, tmp_path, mock_engine):
    task_id, _ = _create(db, tmp_path, "Hello world\nSecond line\nThird line\n")
    ts = TaskService(db)
    # Simulate a partial run: mark segments 0 and 1 as done.
    ts.save_translation(task_id, 0, "bonjour", "bonjour")
    ts.save_translation(task_id, 1, "deux", "deux")
    ts.set_status(task_id, constants.TASK_INTERRUPTED)

    pipeline = TranslationPipeline(db, resume=True)
    result = pipeline.run(task_id)
    assert result["status"] == "completed"

    # Pre-existing translations must be preserved verbatim.
    rows = {r.segment_index: r for r in
            db.query(TaskSegment).filter_by(task_id=task_id).all()}
    assert rows[0].translated_text == "bonjour"
    assert rows[1].translated_text == "deux"
    assert rows[2].status == "done"
    text = Path(result["result_path"]).read_text(encoding="utf-8")
    assert "bonjour" in text


def test_resume_detects_changed_source(db, tmp_path, mock_engine):
    task_id, src = _create(db, tmp_path, "Hello world\n")
    # Change the file after checksum was recorded.
    src.write_text("Hello world\nModified content\n", encoding="utf-8")
    pipeline = TranslationPipeline(db, resume=True)
    try:
        pipeline.run(task_id)
        assert False, "should have refused resume"
    except Exception as exc:
        assert "changé" in str(exc).lower()


def test_mark_interrupted_on_startup(db, tmp_path, mock_engine):
    task_id, _ = _create(db, tmp_path, "Hello\n")
    ts = TaskService(db)
    ts.set_status(task_id, constants.TASK_IN_PROGRESS)
    ts.mark_interrupted()
    assert ts.get(task_id).status == constants.TASK_INTERRUPTED
