from typing import List, Optional

from app.core.logging_config import logger
from app.interfaces.translator import TranslatorInterface


class ArgosTranslator(TranslatorInterface):
    """Local, offline neural translation via Argos Translate.

    Argos uses CTranslate2 / OpenNMT models and requires no network access once
    language packages are installed. This is the default engine for
    confidentiality.
    """

    name = "argos"
    mode = "local"

    def __init__(self):
        self._configured = False
        self.installed_languages = []

    def _ensure(self):
        if self._configured:
            return
        try:
            import argostranslate.translate as _t
            self.installed_languages = _t.get_installed_languages()
        except Exception as exc:
            logger.warning("Argos Translate indisponible: %s", exc)
            self.installed_languages = []
        self._configured = True

    def is_available(self) -> bool:
        self._ensure()
        return len(self.installed_languages) > 0

    def _find_language(self, code: str):
        for lang in self.installed_languages:
            if lang.code == code:
                return lang
        return None

    def supports_pair(self, source_lang: str, target_lang: str) -> bool:
        self._ensure()
        if not source_lang or not target_lang:
            return False
        src = self._find_language(source_lang)
        if not src:
            return False
        return any(t.to_lang.code == target_lang for t in src.translations_from)

    def translate(self, text: str, source_lang: Optional[str], target_lang: str) -> str:
        self._ensure()
        if not text.strip():
            return text
        try:
            import argostranslate.translate as _t
            if source_lang:
                return _t.translate(text, source_lang, target_lang)
            # No declared source: let Argos detect.
            return _t.translate(text, "auto", target_lang)
        except Exception as exc:
            logger.warning("Traduction Argos échouée (%s->%s): %s",
                           source_lang, target_lang, exc)
            return text

    def detect(self, text: str) -> Optional[str]:
        try:
            from app.services.language_detector import detector
            return detector.detect(text)
        except Exception:
            return None

    def get_supported_languages(self) -> List[str]:
        self._ensure()
        langs = set()
        for lang in self.installed_languages:
            langs.add(lang.code)
            for t in lang.translations_from:
                langs.add(t.to_lang.code)
        return sorted(langs)
