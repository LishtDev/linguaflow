import json
from pathlib import Path
from typing import Any, Dict

from app.core.config import settings
from app.core.logging_config import logger, redact

CONFIG_FILE = settings.DATA_DIR / "user_config.json"

DEFAULT_USER_CONFIG: Dict[str, Any] = {
    "default_target_lang": "fr",
    "preferred_engine": "argos",
    "local_engine": "argos",
    "remote_enabled": False,
    "remote_endpoint": "",
    "remote_api_key": "",
    "correction_enabled": False,
    "ocr_enabled": True,
    "allow_auto_download": False,
    "max_file_size_mb": 50,
    "remote_consent": False,
}


class ConfigService:
    """Persistent user configuration stored outside the source tree."""

    def __init__(self, path: Path = CONFIG_FILE):
        self.path = path
        self._cache: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        data = dict(DEFAULT_USER_CONFIG)
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data.update(json.load(f))
            except Exception as exc:
                logger.warning("Configuration illisible, valeurs par défaut: %s", exc)
        self._cache = data
        return data

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._cache.get(key, default)

    def all(self) -> Dict[str, Any]:
        # Never expose the raw API key except internally.
        return dict(self._cache)

    def public(self) -> Dict[str, Any]:
        data = dict(self._cache)
        if data.get("remote_api_key"):
            data["remote_api_key"] = redact(data["remote_api_key"])
            data["remote_api_key_set"] = True
        else:
            data["remote_api_key_set"] = False
        return data

    def update(self, values: Dict[str, Any]) -> None:
        for k, v in values.items():
            if k in DEFAULT_USER_CONFIG:
                self._cache[k] = v
        self.save()


config_service = ConfigService()
