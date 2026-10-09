from pathlib import Path
from typing import List

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter

import openpyxl


class XlsxFormatter(BaseFormatter):
    """XLSX: translate textual cell values only.

    Formulas, references, styles, sheets, defined names and tables are
    preserved because we only overwrite the ``value`` of selected string
    cells and save the original workbook.
    """

    extensions = (".xlsx", ".xlsm")

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        options = options or {}
        wb = openpyxl.load_workbook(str(file_path), data_only=False, keep_links=True)
        sheets = options.get("sheets")  # None = all
        segments: List[Segment] = []
        warnings: List[str] = []
        idx = 0

        for ws in wb.worksheets:
            if sheets and ws.title not in sheets:
                continue
            for row in ws.iter_rows():
                for cell in row:
                    value = cell.value
                    if value is None:
                        continue
                    if isinstance(value, str) and value.startswith("="):
                        continue  # formula - preserve
                    if not isinstance(value, str):
                        continue  # numbers, dates, booleans - preserve
                    if not value.strip():
                        continue
                    segments.append(Segment(
                        index=idx, text=value,
                        ref=(ws.title, cell.coordinate),
                        meta={"data_type": cell.data_type},
                    ))
                    idx += 1

        return ExtractionResult(
            segments=segments,
            structure={"segments": segments},
            warnings=warnings,
        )

    def reconstruct(self, original_path, translations, structure, output_path):
        wb = openpyxl.load_workbook(str(original_path), data_only=False, keep_links=True)
        by_sheet = {}
        for seg in structure.get("segments", []):
            tr = translations.get(seg.index)
            if tr is None:
                continue
            sheet, coord = seg.ref
            by_sheet.setdefault(sheet, {})[coord] = tr

        for sheet_name, cells in by_sheet.items():
            if sheet_name not in wb.sheetnames:
                continue
            ws = wb[sheet_name]
            for coord, tr in cells.items():
                cell = ws[coord]
                # Never overwrite a formula.
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    continue
                cell.value = tr

        wb.save(str(output_path))
        return output_path
