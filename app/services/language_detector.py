from typing import Optional

from app.core.logging_config import logger

try:
    from langdetect import detect, detect_langs, LangDetectException
    _LANGDETECT_AVAILABLE = True
except Exception:  # pragma: no cover
    _LANGDETECT_AVAILABLE = False


# Map ISO 639-1 (langdetect) -> display names (French UI)
LANGUAGE_NAMES_FR = {
    "fr": "Français",
    "en": "Anglais",
    "es": "Espagnol",
    "de": "Allemand",
    "it": "Italien",
    "pt": "Portugais",
    "nl": "Néerlandais",
    "ru": "Russe",
    "zh-cn": "Chinois",
    "zh-tw": "Chinois (traditionnel)",
    "ja": "Japonais",
    "ko": "Coréen",
    "ar": "Arabe",
    "pl": "Polonais",
    "sv": "Suédois",
    "da": "Danois",
    "no": "Norvégien",
    "fi": "Finnois",
    "cs": "Tchèque",
    "ro": "Roumain",
    "hu": "Hongrois",
    "el": "Grec",
    "tr": "Turc",
    "uk": "Ukrainien",
}


def language_name(code: Optional[str]) -> str:
    if not code:
        return "Inconnue"
    return LANGUAGE_NAMES_FR.get(code.lower(), code)


class LanguageDetector:
    """Automatic source-language detection with graceful degradation."""

    def detect(self, text: str) -> Optional[str]:
        if not text or len(text.strip()) < 3:
            return None
        if not _LANGDETECT_AVAILABLE:
            return None
        try:
            code = detect(text[:5000])
            return code
        except LangDetectException:
            return None
        except Exception as exc:  # pragma: no cover
            logger.warning("Détection de langue échouée: %s", exc)
            return None

    def detect_with_confidence(self, text: str):
        if not text or len(text.strip()) < 3 or not _LANGDETECT_AVAILABLE:
            return []
        try:
            results = detect_langs(text[:5000])
            return [(r.lang, r.prob) for r in results]
        except Exception:
            return []


detector = LanguageDetector()
