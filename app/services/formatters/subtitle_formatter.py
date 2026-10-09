import re
from pathlib import Path
from typing import List

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter

TIMESTAMP_RE = re.compile(
    r"^\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})(.*)$"
)
# Reading-speed threshold (characters per second) commonly used for subtitles.
CPS_WARN = 20.0


def _to_seconds(ts: str) -> float:
    ts = ts.replace(",", ".")
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


class SubtitleFormatter(BaseFormatter):
    """SRT / WebVTT: translate cue text, preserve timestamps and structure."""

    extensions = (".srt", ".vtt")

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        content, encoding = self.read_text(file_path)
        lines = content.split("\n")
        segments: List[Segment] = []
        warnings: List[str] = []
        blocks: List[dict] = []
        idx = 0
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            m = TIMESTAMP_RE.match(line)
            if m:
                # Collect text lines until blank line.
                j = i + 1
                text_lines = []
                while j < n and lines[j].strip() != "":
                    text_lines.append(lines[j])
                    j += 1
                text = "\n".join(text_lines)
                start, end = _to_seconds(m.group(1)), _to_seconds(m.group(2))
                duration = max(0.001, end - start)
                seg = Segment(index=idx, text=text, ref=len(blocks),
                              meta={"start_line": i + 1, "end_line": j,
                                    "duration": duration})
                segments.append(seg)
                blocks.append({"start_line": i + 1, "end_line": j, "segment": seg})
                idx += 1
                i = j
            else:
                i += 1

        # Reading-speed warnings.
        for seg in segments:
            cps = len(seg.text.replace("\n", " ")) / seg.meta["duration"]
            if cps > CPS_WARN:
                warnings.append(
                    f"Segment {seg.index + 1}: lecture rapide possible "
                    f"({cps:.0f} car/s)."
                )

        return ExtractionResult(
            segments=segments,
            structure={"lines": lines, "encoding": encoding, "segments": segments,
                       "blocks": blocks},
            warnings=list(dict.fromkeys(warnings)),
        )

    def reconstruct(self, original_path, translations, structure, output_path):
        lines = list(structure["lines"])
        encoding = structure.get("encoding", "utf-8")
        # Process bottom-up so line indices remain valid.
        for seg in sorted(structure.get("segments", []),
                          key=lambda s: s.meta["start_line"], reverse=True):
            tr = translations.get(seg.index)
            if tr is None:
                continue
            sl = seg.meta["start_line"]
            el = seg.meta["end_line"]
            lines[sl:el] = tr.split("\n")
        output_path.write_text("\n".join(lines), encoding=encoding)
        return output_path
