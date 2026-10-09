from pathlib import Path

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter


class TxtFormatter(BaseFormatter):
    """Plain text: preserve line breaks and encoding."""

    extensions = (".txt",)

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        content, encoding = self.read_text(file_path)
        lines = content.splitlines(keepends=False)
        segments = []
        idx = 0
        for lineno, line in enumerate(lines):
            if line.strip():
                segments.append(Segment(index=idx, text=line, ref=lineno))
                idx += 1
        return ExtractionResult(
            segments=segments,
            structure={"lines": lines, "encoding": encoding, "segments": segments,
                       "trailing_newline": content.endswith("\n")},
        )

    def reconstruct(self, original_path, translations, structure, output_path):
        lines = list(structure["lines"])
        encoding = structure.get("encoding", "utf-8")
        for seg in structure.get("segments", []):
            if seg.ref is not None and seg.ref < len(lines):
                lines[seg.ref] = translations.get(seg.index, lines[seg.ref])
        text = "\n".join(lines)
        if structure.get("trailing_newline") and not text.endswith("\n"):
            text += "\n"
        output_path.write_text(text, encoding=encoding)
        return output_path
