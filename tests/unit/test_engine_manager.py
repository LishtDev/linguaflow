import pytest

from app.core.exceptions import EngineUnavailableError, RemoteEngineDisabledError
from app.services.config_service import config_service
from app.services.translation.engine_manager import engine_manager


def test_list_engines_includes_argos_and_remote():
    ids = [e["id"] for e in engine_manager.list_engines()]
    assert "argos" in ids
    assert "libretranslate" in ids


def test_argos_is_local_and_remote_requires_consent():
    engines = {e["id"]: e for e in engine_manager.list_engines()}
    assert engines["argos"]["mode"] == "local"
    assert engines["libretranslate"]["mode"] == "remote"
    assert engines["libretranslate"]["requires_consent"] is True


def test_remote_disabled_by_default():
    with pytest.raises(RemoteEngineDisabledError):
        engine_manager.select(requested="libretranslate", consent=True)


def test_remote_requires_consent_even_when_enabled(monkeypatch):
    monkeypatch.setattr(config_service, "_cache", {
        **config_service.all(),
        "remote_enabled": True,
        "remote_endpoint": "http://127.0.0.1:5000",
    })
    with pytest.raises(RemoteEngineDisabledError):
        engine_manager.select(requested="libretranslate", consent=False)


def test_unknown_engine_raises():
    with pytest.raises(EngineUnavailableError):
        engine_manager.select(requested="nope")
