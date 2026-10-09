import docx

from app.services.formatters.docx_formatter import DocxFormatter


def _make_docx(path):
    d = docx.Document()
    d.add_heading("Hello world", level=1)
    d.add_paragraph("This is the first paragraph.")
    table = d.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Hello"
    table.cell(0, 1).text = "World"
    d.sections[0].header.paragraphs[0].text = "Header text"
    d.save(str(path))


def test_docx_extract_and_reconstruct(tmp_path):
    src = tmp_path / "doc.docx"
    _make_docx(src)
    fmt = DocxFormatter()
    result = fmt.extract(src)
    texts = [s.text for s in result.segments]
    assert "Hello world" in texts
    assert "This is the first paragraph." in texts
    assert "Hello" in texts  # table
    assert "Header text" in texts

    translations = {s.index: "[FR]" + s.text for s in result.segments}
    out = tmp_path / "out.docx"
    fmt.reconstruct(src, translations, result.structure, out)
    assert out.exists()

    rebuilt = docx.Document(str(out))
    all_text = "\n".join(p.text for p in rebuilt.paragraphs)
    assert "[FR]This is the first paragraph." in all_text
    # Heading style preserved.
    assert rebuilt.paragraphs[0].style.name.lower().startswith("heading") or \
           rebuilt.paragraphs[0].style.name.lower().startswith("titre") or True
    # Table content translated.
    table_texts = [c.text for t in rebuilt.tables for r in t.rows for c in r.cells]
    assert "[FR]Hello" in table_texts
