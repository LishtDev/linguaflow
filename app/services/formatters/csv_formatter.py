import csv
from pathlib import Path

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter


class CsvFormatter(BaseFormatter):
    """CSV/TSV: preserve delimiter, encoding, column order and non-text values.

    Translation is limited to selected columns (default: all text-looking
    columns). Numeric / formula cells are never touched.
    """

    extensions = (".csv", ".tsv")

    def _sniff(self, sample: str, default=",") -> str:
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            return dialect.delimiter
        except Exception:
            return "\t" if sample.count("\t") > sample.count(",") else default

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        options = options or {}
        content, encoding = self.read_text(file_path)
        delimiter = options.get("delimiter") or self._sniff(content[:4096])
        rows = list(csv.reader(content.splitlines(), delimiter=delimiter))
        if not rows:
            return ExtractionResult(segments=[], structure={"rows": [], "delimiter": delimiter})

        has_header = options.get("has_header", True)
        data_rows = rows[1:] if has_header else rows

        ncols = max((len(r) for r in rows), default=0)
        selected = options.get("columns")
        if selected is None:
            # Default: columns that contain at least one non-numeric value.
            selected = []
            for c in range(ncols):
                for r in data_rows:
                    if c < len(r) and r[c].strip() and not self._is_numeric(r[c]):
                        selected.append(c)
                        break
        selected = set(int(c) for c in selected)

        segments = []
        idx = 0
        for ri, row in enumerate(data_rows):
            for ci, cell in enumerate(row):
                if ci in selected and cell.strip() and not self._is_numeric(cell):
                    segments.append(Segment(index=idx, text=cell, ref=(ri, ci)))
                    idx += 1

        return ExtractionResult(
            segments=segments,
            structure={
                "rows": rows,
                "delimiter": delimiter,
                "encoding": encoding,
                "has_header": has_header,
                "columns": sorted(selected),
                "segments": segments,
                "trailing_newline": content.endswith("\n"),
            },
        )

    def reconstruct(self, original_path, translations, structure, output_path):
        delimiter = structure["delimiter"]
        has_header = structure["has_header"]
        data_rows = structure["rows"][1:] if has_header else structure["rows"]
        for seg in structure.get("segments", []):
            tr = translations.get(seg.index)
            if tr is None:
                continue
            ri, ci = seg.ref
            if ri < len(data_rows) and ci < len(data_rows[ri]):
                data_rows[ri][ci] = tr

        out_rows = ([structure["rows"][0]] if has_header else []) + data_rows
        with open(output_path, "w", encoding=structure.get("encoding", "utf-8"),
                  newline="") as f:
            writer = csv.writer(f, delimiter=delimiter,
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerows(out_rows)
        return output_path

    @staticmethod
    def _is_numeric(value: str) -> bool:
        v = value.strip()
        if not v:
            return False
        if v.startswith("="):  # formula
            return True
        try:
            float(v.replace(",", ".").replace(" ", "").replace("%", ""))
            return True
        except ValueError:
            return False
