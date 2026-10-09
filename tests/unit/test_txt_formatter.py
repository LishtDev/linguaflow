from app.services.formatters.txt_formatter import TxtFormatter


def test_txt_extract_preserves_lines(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("Hello world\n\nSecond paragraph\n", encoding="utf-8")
    result = TxtFormatter().extract(f)
    texts = [s.text for s in result.segments]
    assert "Hello world" in texts
    assert "Second paragraph" in texts
    assert len(result.segments) == 2


def test_txt_reconstruct_roundtrip(tmp_path):
    f = tmp_path / "sample.txt"
    original = "Hello world\n\nSecond paragraph\n"
    f.write_text(original, encoding="utf-8")
    fmt = TxtFormatter()
    result = fmt.extract(f)
    translations = {s.index: s.text.upper() for s in result.segments}
    out = tmp_path / "out.txt"
    fmt.reconstruct(f, translations, result.structure, out)
    content = out.read_text(encoding="utf-8")
    assert "HELLO WORLD" in content
    assert "SECOND PARAGRAPH" in content
    assert content.count("\n") == original.count("\n")


def test_txt_handles_accents(tmp_path):
    f = tmp_path / "acc.txt"
    f.write_text("Déjà vu à Noël", encoding="latin-1")
    result = TxtFormatter().extract(f)
    assert "Déjà" in result.segments[0].text
