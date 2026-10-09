from pathlib import Path

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter
from app.services.ocr.ocr_service import OcrService


class ImageFormatter(BaseFormatter):
    """Images: extract text with local OCR, export translated text.

    Visual reconstruction of the image is a separate, harder problem and is
    intentionally not claimed as fully supported: the result is a translated
    text file alongside the original image.
    """

    extensions = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")

    def __init__(self):
        self.ocr = OcrService()

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        options = options or {}
        text = self.ocr.extract_text(file_path, lang=options.get("lang"))
        # Split into paragraph-like units.
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        if not blocks:
            blocks = [text] if text.strip() else []
        segments = [Segment(index=i, text=b, ref=i) for i, b in enumerate(blocks)]
        warnings = []
        conf = self.ocr.extract_with_confidence(file_path, lang=options.get("lang"))
        low = sum(1 for w in conf["words"] if w["conf"] < 60)
        if low:
            warnings.append(
                f"{low} mot(s) reconnus avec une confiance faible : "
                "une relecture est conseillée."
            )
        return ExtractionResult(
            segments=segments,
            structure={"segments": segments, "original_image": str(file_path)},
            warnings=warnings,
        )

    def reconstruct(self, original_path, translations, structure, output_path):
        text = "\n\n".join(translations.get(s.index, s.text)
                           for s in structure.get("segments", []))
        # Result is a text file describing the OCR translation.
        out = output_path.with_suffix(".txt")
        out.write_text(text, encoding="utf-8")
        return out
