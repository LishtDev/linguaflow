from app.services.formatters.html_formatter import HtmlFormatter


HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Hello world</title>
  <script>var x = "do not translate";</script>
  <style>.a { color: red; }</style>
</head>
<body>
  <h1 title="Hello title">Hello body</h1>
  <img src="pic.png" alt="Hello image">
  <p>Some <b>bold</b> text.</p>
</body>
</html>
"""


def test_html_extracts_visible_text(tmp_path):
    f = tmp_path / "page.html"
    f.write_text(HTML, encoding="utf-8")
    result = HtmlFormatter().extract(f)
    texts = [s.text for s in result.segments]
    assert "Hello body" in texts
    assert "Hello world" in texts  # <title>
    assert "Hello title" in texts  # title attribute
    assert "Hello image" in [t for s in result.segments for t in [s.text] if "image" in s.text][0] or \
        any("Hello image" == t for t in texts)
    # script/style content must never be extracted.
    assert "do not translate" not in "\n".join(texts)
    assert "color: red" not in "".join(texts)


def test_html_preserves_tags(tmp_path):
    f = tmp_path / "doc.html"
    f.write_text(HTML, encoding="utf-8")
    fmt = HtmlFormatter()
    result = fmt.extract(f)
    translations = {s.index: (s.text.replace("Hello", "Bonjour")) for s in result.segments}
    out = tmp_path / "out.html"
    fmt.reconstruct(f, translations, result.structure, out)
    content = out.read_text(encoding="utf-8")
    assert "<h1" in content
    assert 'alt="Bonjour image"' in content
    assert "var x = \"do not translate\";" in content  # script untouched
    assert "Bonjour body" in content
