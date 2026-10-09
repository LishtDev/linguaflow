from pathlib import Path
from typing import Dict, List

from app.core.exceptions import UnsupportedFormatError
from app.interfaces.formatter import FormatterInterface
from app.services.formatters.csv_formatter import CsvFormatter
from app.services.formatters.doc_formatter import DocFormatter
from app.services.formatters.docx_formatter import DocxFormatter
from app.services.formatters.epub_formatter import EpubFormatter
from app.services.formatters.html_formatter import HtmlFormatter
from app.services.formatters.image_formatter import ImageFormatter
from app.services.formatters.markdown_formatter import MarkdownFormatter
from app.services.formatters.pdf_formatter import PdfFormatter
from app.services.formatters.pptx_formatter import PptxFormatter
from app.services.formatters.subtitle_formatter import SubtitleFormatter
from app.services.formatters.txt_formatter import TxtFormatter
from app.services.formatters.xlsx_formatter import XlsxFormatter


class FormatterRegistry:
    """Maps file extensions to their specialized formatter."""

    def __init__(self):
        self._formatters: Dict[str, FormatterInterface] = {}
        self._register(TxtFormatter())
        self._register(MarkdownFormatter())
        self._register(HtmlFormatter())
        self._register(CsvFormatter())
        self._register(DocxFormatter())
        self._register(DocFormatter())
        self._register(PptxFormatter())
        self._register(XlsxFormatter())
        self._register(PdfFormatter())
        self._register(EpubFormatter())
        self._register(SubtitleFormatter())
        self._register(ImageFormatter())

    def _register(self, formatter: FormatterInterface) -> None:
        for ext in formatter.extensions:
            self._formatters[ext.lstrip(".")] = formatter

    def get_for_path(self, path: Path) -> FormatterInterface:
        ext = Path(path).suffix.lower().lstrip(".")
        if ext not in self._formatters:
            raise UnsupportedFormatError(f"Format non pris en charge : '{ext}'")
        return self._formatters[ext]

    def supported_extensions(self) -> List[str]:
        return sorted(self._formatters.keys())

    def describe(self) -> List[dict]:
        seen = {}
        for ext, fmt in self._formatters.items():
            seen.setdefault(fmt.__class__.__name__, []).append(ext)
        return [
            {"formatter": name, "extensions": sorted(exts)}
            for name, exts in sorted(seen.items())
        ]


registry = FormatterRegistry()
