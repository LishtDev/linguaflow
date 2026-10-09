import re
from pathlib import Path

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})(\s+)(.*)$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)(.*)$")
QUOTE_RE = re.compile(r"^(\s*>+\s?)(.*)$")
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]*)\)")


class MarkdownFormatter(BaseFormatter):
    """Markdown: translate visible prose, preserve syntax and code."""

    extensions = (".md", ".markdown")

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        content, encoding = self.read_text(file_path)
        lines = content.split("\n")
        segments = []
        idx = 0
        in_fence = False
        fence_marker = ""

        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                marker = FENCE_RE.match(line).group(1)
                if not in_fence:
                    in_fence = True
                    fence_marker = marker
                elif marker == fence_marker:
                    in_fence = False
                continue
            if in_fence:
                continue
            if TABLE_RE.match(line):
                # Translate each cell separately, keep pipes.
                cells = line.strip().strip("|").split("|")
                if all(set(c.strip()) <= set("-: ") for c in cells):
                    continue  # separator row
                for j, cell in enumerate(cells):
                    cell_text = cell.strip()
                    if cell_text:
                        segments.append(Segment(index=idx, text=cell_text,
                                                ref=(i, j), meta={"sep": True}))
                        idx += 1
                continue

            m = HEADING_RE.match(line)
            if m:
                segments.append(Segment(index=idx, text=m.group(3),
                                        ref=i, meta={"prefix": m.group(1) + m.group(2)}))
                idx += 1
                continue
            m = LIST_RE.match(line)
            if m:
                segments.append(Segment(index=idx, text=m.group(4),
                                        ref=i,
                                        meta={"prefix": m.group(1) + m.group(2) + m.group(3)}))
                idx += 1
                continue
            m = QUOTE_RE.match(line)
            if m:
                segments.append(Segment(index=idx, text=m.group(2),
                                        ref=i, meta={"prefix": m.group(1)}))
                idx += 1
                continue
            if line.strip():
                segments.append(Segment(index=idx, text=line, ref=i, meta={}))
                idx += 1

        return ExtractionResult(
            segments=segments,
            structure={"lines": lines, "encoding": encoding, "segments": segments},
        )

    def reconstruct(self, original_path, translations, structure, output_path):
        lines = list(structure["lines"])
        encoding = structure.get("encoding", "utf-8")
        # Group table cells by line.
        table_rows = {}
        for seg in structure.get("segments", []):
            tr = translations.get(seg.index)
            if tr is None:
                continue
            if seg.meta.get("sep") and isinstance(seg.ref, tuple):
                table_rows.setdefault(seg.ref[0], {})[seg.ref[1]] = tr
            else:
                prefix = seg.meta.get("prefix", "")
                lines[seg.ref] = prefix + tr

        for lineno, cells in table_rows.items():
            orig = lines[lineno].strip().strip("|").split("|")
            rebuilt = []
            for j, cell in enumerate(orig):
                if j in cells:
                    rebuilt.append(" " + cells[j] + " ")
                else:
                    rebuilt.append(cell)
            lines[lineno] = "|" + "|".join(rebuilt) + "|"

        output_path.write_text("\n".join(lines), encoding=encoding)
        return output_path
