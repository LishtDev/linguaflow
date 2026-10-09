from typing import List, Optional

from app.core.exceptions import RemoteEngineDisabledError
from app.core.logging_config import logger
from app.interfaces.translator import TranslatorInterface


class LibreTranslateTranslator(TranslatorInterface):
    """Optional remote engine (LibreTranslate-compatible HTTP API).

    Disabled unless explicitly configured by the user. No document is ever
    sent here automatically: the orchestrator enforces user consent.
    """

    name = "libretranslate"
    mode = "remote"

    def __init__(self, endpoint: str = "", api_key: str = "", enabled: bool = False,
                 timeout: int = 30):
        self.endpoint = (endpoint or "").rstrip("/")
        self.api_key = api_key or ""
        self.enabled = enabled
        self.timeout = timeout

    def is_available(self) -> bool:
        return bool(self.enabled and self.endpoint)

    def _client(self):
        import httpx
        return httpx.Client(timeout=self.timeout)

    def translate(self, text: str, source_lang: Optional[str], target_lang: str) -> str:
        if not self.is_available():
            raise RemoteEngineDisabledError(
                "Le moteur distant est désactivé ou non configuré."
            )
        if not text.strip():
            return text
        payload = {
            "q": text,
            "source": source_lang or "auto",
            "target": target_lang,
            "format": "text",
        }
        if self.api_key:
            payload["api_key"] = self.api_key
        try:
            with self._client() as client:
                resp = client.post(f"{self.endpoint}/translate", json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("translatedText", text)
        except Exception as exc:
            logger.warning("Traduction distante échouée: %s", exc)
            return text

    def get_supported_languages(self) -> List[str]:
        if not self.is_available():
            return []
        try:
            with self._client() as client:
                resp = client.get(f"{self.endpoint}/languages")
                resp.raise_for_status()
                return [l["code"] for l in resp.json()]
        except Exception:
            return []
