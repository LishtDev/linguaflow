import os
import re
import tempfile
from pathlib import Path

import pytest

# Isolate test data before importing the app.
_TEST_DIR = Path(tempfile.mkdtemp(prefix="linguaflow_test_"))
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DIR}/test.db"

from app.core.config import settings  # noqa: E402

settings.DATA_DIR = _TEST_DIR
settings.TEMP_DIR = _TEST_DIR / "temp"
settings.RESULTS_DIR = _TEST_DIR / "results"
settings.CACHE_DIR = _TEST_DIR / "cache"
for _d in (settings.DATA_DIR, settings.TEMP_DIR, settings.RESULTS_DIR, settings.CACHE_DIR):
    _d.mkdir(parents=True, exist_ok=True)


class MockTranslator:
    """Deterministic engine for tests. Performs no I/O whatsoever."""

    name = "mock"
    mode = "local"

    DICT = {
        "hello": "bonjour",
        "world": "monde",
        "the": "le",
        "quick": "rapide",
        "brown": "brun",
        "fox": "renard",
        "cup of tea": "truc",
        "up to you": "à toi de décider",
        "get the ball rolling": "lancer les choses",
        "hello world": "bonjour le monde",
    }

    def is_available(self):
        return True

    def supports_pair(self, s, t):
        return True

    def get_supported_languages(self):
        return ["en", "fr"]

    def detect(self, text):
        return "en"

    def translate(self, text, source_lang=None, target_lang="fr"):
        stripped = text.strip()
        low = stripped.lower()
        if low in self.DICT:
            # Preserve surrounding whitespace.
            return text.replace(stripped, self.DICT[low])
        out = text
        for k, v in self.DICT.items():
            out = re.sub(rf"\b{re.escape(k)}\b", v, out, flags=re.IGNORECASE)
        if out == text and stripped:
            out = "[FR]" + text
        return out


@pytest.fixture
def mock_engine(monkeypatch):
    engine = MockTranslator()
    import app.services.translation_service as ts
    monkeypatch.setattr(ts.engine_manager, "select", lambda **kw: engine)
    return engine


@pytest.fixture
def db():
    from app.core.database import SessionLocal, init_db
    init_db()
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
