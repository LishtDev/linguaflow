from pathlib import Path
from typing import List

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter

try:
    import pymupdf as fitz
except ImportError:  # older versions expose "fitz"
    import fitz


class PdfFormatter(BaseFormatter):
    """Textual PDF: extract positioned text blocks, translate and re-insert.

    Best-effort layout preservation: original text is removed per block and the
    translation is drawn into the same rectangle, shrinking the font to fit.
    Complex layouts (columns, tables, embedded fonts) may not be perfect; such
    cases are reported as warnings.
    """

    extensions = (".pdf",)

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        doc = fitz.open(str(file_path))
        segments: List[Segment] = []
        warnings: List[str] = []
        idx = 0
        for pno in range(doc.page_count):
            blocks = doc[pno].get_text("blocks")
            for b in blocks:
                x0, y0, x1, y1, text, _no, btype = b
                if btype != 0:
                    continue
                if not text.strip():
                    continue
                segments.append(Segment(
                    index=idx, text=text,
                    ref=(pno, idx, (x0, y0, x1, y1)),
                ))
                idx += 1
        if not segments:
            warnings.append(
                "Aucun texte natif détecté dans le PDF. "
                "Il s'agit peut-être d'un PDF scanné : utilisez l'OCR."
            )
        doc.close()
        return ExtractionResult(segments=segments, structure={"segments": segments},
                                warnings=warnings)

    def reconstruct(self, original_path, translations, structure, output_path):
        doc = fitz.open(str(original_path))
        # Group segments by page.
        by_page = {}
        for seg in structure.get("segments", []):
            tr = translations.get(seg.index)
            if tr is None:
                continue
            pno, _, bbox = seg.ref
            by_page.setdefault(pno, []).append((bbox, tr))

        for pno, items in by_page.items():
            page = doc[pno]
            for bbox, tr in items:
                rect = fitz.Rect(*bbox)
                self._redact(page, rect)
            try:
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            except TypeError:
                page.apply_redactions()
            for bbox, tr in items:
                rect = fitz.Rect(*bbox)
                self._insert_fitted(page, rect, tr)

        doc.save(str(output_path), garbage=4, deflate=True)
        doc.close()
        return output_path

    @staticmethod
    def _redact(page, rect):
        annot = page.add_redact_annot(rect)
        annot.update()

    @staticmethod
    def _insert_fitted(page, rect, text):
        size = max(6, min(12, rect.height / max(1, _count_lines(text))))
        while size >= 5:
            rc = page.insert_textbox(
                rect, text, fontsize=size, fontname="helv",
                color=(0, 0, 0), align=0,
            )
            if rc >= 0:
                return
            size -= 0.5
        # Last resort: insert at point even if it overflows.
        page.insert_text((rect.x0, rect.y0 + 10), text, fontsize=8, fontname="helv")


def _count_lines(text: str) -> int:
    return max(1, text.count("\n") + 1)
