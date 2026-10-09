import hashlib
import re
import uuid
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import FileValidationError, FileTooLargeError, UnsupportedFormatError

SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(name: str) -> str:
    """Return a filesystem-safe filename derived from an untrusted name."""
    name = Path(name).name  # strip any directory components
    name = SAFE_NAME_RE.sub("_", name).strip("._") or "document"
    return name[:180]


def new_task_id() -> str:
    return uuid.uuid4().hex


def secure_temp_path(original_name: str) -> Path:
    """Create a unique path inside the managed temp dir (no traversal)."""
    safe = sanitize_filename(original_name)
    token = uuid.uuid4().hex
    return settings.TEMP_DIR / f"{token}_{safe}"


def result_path_for(task_id: str, original_name: str) -> Path:
    safe = sanitize_filename(original_name)
    stem = Path(safe).stem
    suffix = Path(safe).suffix
    return settings.RESULTS_DIR / f"{task_id}__{stem}_fr{suffix}"


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    if not ext or ext not in settings.allowed_extensions:
        raise UnsupportedFormatError(f"Format non pris en charge : '{ext or 'inconnu'}'")
    return ext


def validate_size(path: Path) -> None:
    size = path.stat().st_size
    if size == 0:
        raise FileValidationError("Le fichier est vide.")
    if size > settings.MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(
            f"Fichier trop volumineux ({size / 1048576:.1f} Mo). "
            f"Limite : {settings.MAX_FILE_SIZE_MB} Mo."
        )


def is_within(base: Path, candidate: Path) -> bool:
    """Guard against directory traversal."""
    base = base.resolve()
    try:
        candidate.resolve().relative_to(base)
        return True
    except ValueError:
        return False
