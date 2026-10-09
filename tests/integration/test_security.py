import pytest

from app.core.security import (is_within, sanitize_filename, validate_extension,
                              validate_size, secure_temp_path)
from app.core.exceptions import (FileTooLargeError, UnsupportedFormatError,
                                 FileValidationError)
from app.core.config import settings


def test_sanitize_filename_strips_paths():
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("/absolute/path/file.txt") == "file.txt"
    assert sanitize_filename("weird<>name?.txt").startswith("weird")


def test_validate_extension_rejects_unknown():
    with pytest.raises(UnsupportedFormatError):
        validate_extension("virus.exe")
    assert validate_extension("doc.TXT") == "txt"
    assert validate_extension("file.docx") == "docx"


def test_is_within_blocks_traversal(tmp_path):
    base = tmp_path / "results"
    base.mkdir()
    inside = base / "ok.txt"
    inside.write_text("x")
    assert is_within(base, inside) is True
    outside = tmp_path / "secret.txt"
    outside.write_text("x")
    assert is_within(base, outside) is False
    assert is_within(base, base / ".." / "secret.txt") is False


def test_secure_temp_path_is_managed_dir():
    p = secure_temp_path("../../evil.txt")
    assert settings.TEMP_DIR in p.parents or p.parent == settings.TEMP_DIR
    assert ".." not in str(p)


def test_validate_size_rejects_empty(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")
    with pytest.raises(FileValidationError):
        validate_size(f)


def test_validate_size_rejects_oversize(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE_BYTES", 5)
    f = tmp_path / "big.txt"
    f.write_text("too many bytes here")
    with pytest.raises(FileTooLargeError):
        validate_size(f)
