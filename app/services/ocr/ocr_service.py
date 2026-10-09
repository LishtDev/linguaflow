from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.exceptions import ExtractionError

try:
    import pytesseract
    from PIL import Image
    _OCR_AVAILABLE = True
except Exception:  # pragma: no cover
    _OCR_AVAILABLE = False
    pytesseract = None
    Image = None


class OcrService:
    """Local OCR using Tesseract. Never sends images anywhere."""

    def __init__(self, lang: str = None):
        self.lang = lang or settings.TESSERACT_LANG

    def is_available(self) -> bool:
        if not _OCR_AVAILABLE:
            return False
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def available_languages(self) -> List[str]:
        if not self.is_available():
            return []
        try:
            return pytesseract.get_languages(config="")
        except Exception:
            return []

    def _resolve_lang(self, requested: Optional[str]) -> str:
        langs = self.available_languages()
        if requested and requested in langs:
            return requested
        # Prefer fra+eng if present.
        have = [l for l in ("fra", "eng") if l in langs]
        return "+".join(have) if have else (langs[0] if langs else "eng")

    def extract_text(self, image_path: Path, lang: Optional[str] = None) -> str:
        if not self.is_available():
            raise ExtractionError(
                "OCR indisponible : installez Tesseract et pytesseract "
                "(sudo apt install tesseract-ocr tesseract-ocr-fra)."
            )
        image = Image.open(str(image_path))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        data = pytesseract.image_to_string(image, lang=self._resolve_lang(lang))
        return data

    def extract_with_confidence(self, image_path: Path,
                                lang: Optional[str] = None) -> Dict:
        """Return text plus per-word confidence for uncertainty reporting."""
        if not self.is_available():
            raise ExtractionError("OCR indisponible (Tesseract non installé).")
        image = Image.open(str(image_path))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        data = pytesseract.image_to_data(
            image, lang=self._resolve_lang(lang),
            output_type=pytesseract.Output.DICT,
        )
        words = []
        n = len(data.get("text", []))
        low_conf = 0
        for i in range(n):
            word = (data["text"][i] or "").strip()
            if not word:
                continue
            conf = float(data["conf"][i]) if data["conf"][i] not in ("-1", -1) else 0.0
            words.append({"text": word, "conf": conf,
                          "left": data["left"][i], "top": data["top"][i],
                          "width": data["width"][i], "height": data["height"][i]})
            if conf and conf < 60:
                low_conf += 1
        return {
            "text": " ".join(w["text"] for w in words),
            "words": words,
            "low_confidence_words": low_conf,
        }

    def reconstruct_image(self, image_path: Path, translations: str,
                          output_path: Path) -> Path:
        """Produce a sidecar text file with the translated text.

        True visual reconstruction (redrawing translated text over the image
        while preserving the original typography) is a distinct, harder
        feature; this produces a faithful textual export instead.
        """
        out_txt = output_path.with_suffix(".txt")
        out_txt.write_text(translations, encoding="utf-8")
        return out_txt


ocr_service = OcrService()
