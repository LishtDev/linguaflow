"""Generate representative sample documents for manual testing.

Usage:
    python3 scripts/generate_fixtures.py [output_dir]

Creates one small sample per supported format under ``examples/`` (by default).
These files are intentionally tiny and safe to translate.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

SAMPLE_TEXT = (
    "Hello world.\n\n"
    "This tool uses cloud computing and machine learning to translate files.\n\n"
    "Contact admin@example.com or visit https://example.com for the ballpark.\n"
)


def _txt(d: Path) -> None:
    (d / "sample.txt").write_text(SAMPLE_TEXT, encoding="utf-8")


def _markdown(d: Path) -> None:
    (d / "sample.md").write_text(
        "# Project overview\n\n"
        "This is a **bold** statement about machine learning.\n\n"
        "```python\nprint('hello')\n```\n\n"
        "- Item one\n- Item two\n\n"
        "See [documentation](https://example.com/docs).\n",
        encoding="utf-8",
    )


def _html(d: Path) -> None:
    (d / "sample.html").write_text(
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        "<title>Doc</title></head><body>"
        "<h1>Project overview</h1><p>This uses <b>machine learning</b>.</p>"
        "<script>var x = 1;</script></body></html>\n",
        encoding="utf-8",
    )


def _csv(d: Path) -> None:
    with (d / "sample.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "description", "price"])
        w.writerow(["Widget", "A useful device", "19.99"])
        w.writerow(["Gadget", "An improved device", "29.50"])


def _srt(d: Path) -> None:
    (d / "sample.srt").write_text(
        "1\n00:00:01,000 --> 00:00:04,000\nHello everyone.\n\n"
        "2\n00:00:05,000 --> 00:00:08,000\nWelcome to the project.\n",
        encoding="utf-8",
    )


def _vtt(d: Path) -> None:
    (d / "sample.vtt").write_text(
        "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nHello everyone.\n",
        encoding="utf-8",
    )


def _docx(d: Path) -> None:
    from docx import Document
    doc = Document()
    doc.add_heading("Project overview", level=1)
    p = doc.add_paragraph("This tool uses machine learning to translate documents.")
    p.add_run(" Contact: admin@example.com")
    doc.save(str(d / "sample.docx"))


def _xlsx(d: Path) -> None:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws["A1"], ws["B1"], ws["C1"] = "Product", "Description", "Total"
    ws["A2"], ws["B2"], ws["C2"] = "Widget", "A useful device", '=B2&" units"'
    ws["A3"] = 42
    wb.save(str(d / "sample.xlsx"))


def _pptx(d: Path) -> None:
    from pptx import Presentation
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    box = slide.shapes.add_textbox(0, 0, 0, 0)
    box.left, box.top = 914400, 914400
    box.width, box.height = 5486400, 1828800
    tf = box.text_frame
    tf.text = "Project overview"
    tf.add_paragraph().text = "This uses machine learning to translate documents."
    prs.save(str(d / "sample.pptx"))


def _pdf(d: Path) -> None:
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Project overview", fontsize=18)
    page.insert_text((72, 110), "This tool uses machine learning.", fontsize=12)
    page.insert_text((72, 130), "Contact admin@example.com", fontsize=12)
    doc.save(str(d / "sample.pdf"))
    doc.close()


def _epub(d: Path) -> None:
    from ebooklib import epub
    book = epub.EpubBook()
    book.set_identifier("sample-001")
    book.set_title("Sample")
    book.set_language("en")
    ch = epub.EpubHtml(title="Chapter 1", file_name="chap_01.xhtml", lang="en")
    ch.content = ("<h1>Project overview</h1>"
                  "<p>This tool uses machine learning to translate files.</p>")
    book.add_item(ch)
    book.toc = (ch,)
    book.spine = ["nav", ch]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(str(d / "sample.epub"), book)


GENERATORS = {
    "sample.txt": _txt,
    "sample.md": _markdown,
    "sample.html": _html,
    "sample.csv": _csv,
    "sample.srt": _srt,
    "sample.docx": _docx,
    "sample.xlsx": _xlsx,
    "sample.pptx": _pptx,
    "sample.pdf": _pdf,
    "sample.epub": _epub,
}


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples")
    out.mkdir(parents=True, exist_ok=True)
    ok = 0
    for name, fn in GENERATORS.items():
        try:
            fn(out)
            print(f"  OK   {name}")
            ok += 1
        except Exception as exc:  # pragma: no cover - depends on optional deps
            print(f"  FAIL {name}: {exc}")
    print(f"\n{ok}/{len(GENERATORS)} fixtures written to {out.resolve()}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
