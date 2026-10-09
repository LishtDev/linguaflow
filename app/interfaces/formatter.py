from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Segment:
    """A translatable unit extracted from a document."""
    index: int
    text: str
    # Opaque reference used by the formatter to place text back.
    ref: Any = None
    # Properties that constrain translation (e.g. max length).
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    segments: List[Segment]
    structure: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


class FormatterInterface(ABC):
    """Each supported format implements this interface."""

    extensions: tuple = ()

    @abstractmethod
    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        """Read a document and return its translatable segments.

        ``options`` carries format-specific settings, e.g. {"columns": [1, 2]}
        for CSV or {"sheet": "Feuil1"} for XLSX.
        """
        raise NotImplementedError

    @abstractmethod
    def reconstruct(
        self,
        original_path: Path,
        translations: Dict[int, str],
        structure: Dict[str, Any],
        output_path: Path,
    ) -> Path:
        """Rebuild the document with translated segments."""
        raise NotImplementedError
