from app.services.formatters.csv_formatter import CsvFormatter


def test_csv_preserves_structure_and_numeric(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("name,price,note\nApple,1.5,Hello world\nBanana,2,Second item\n",
                 encoding="utf-8")
    fmt = CsvFormatter()
    result = fmt.extract(f)
    # Only textual cells selected; price column excluded by default.
    refs = [s.ref for s in result.segments]
    assert (0, 0) in refs  # Apple
    assert (0, 1) not in refs  # price numeric
    assert (0, 2) in refs  # note

    translations = {s.index: "[FR]" + s.text for s in result.segments}
    out = tmp_path / "out.csv"
    fmt.reconstruct(f, translations, result.structure, out)
    content = out.read_text(encoding="utf-8")
    assert "[FR]Apple" in content
    assert "1.5" in content  # numeric untouched
    assert "[FR]Second item" in content


def test_csv_delimiter_detection_semicolon(tmp_path):
    f = tmp_path / "euro.csv"
    f.write_text("a;b\nHello;World\n", encoding="utf-8")
    fmt = CsvFormatter()
    result = fmt.extract(f)
    assert result.structure["delimiter"] == ";"


def test_csv_formula_not_touched(tmp_path):
    f = tmp_path / "f.csv"
    f.write_text("x,y\nHello,=SUM(A1:A2)\n", encoding="utf-8")
    fmt = CsvFormatter()
    result = fmt.extract(f)
    refs = [s.ref for s in result.segments]
    assert (0, 1) not in refs  # formula not a translatable segment
