from app.services.formatters.markdown_formatter import MarkdownFormatter


MD = """# Hello world

This is a paragraph.

```python
print("hello")
```

- item one
- item two

> A quote here
"""


def test_markdown_preserves_code_and_structure(tmp_path):
    f = tmp_path / "doc.md"
    f.write_text(MD, encoding="utf-8")
    fmt = MarkdownFormatter()
    result = fmt.extract(f)
    texts = [s.text for s in result.segments]
    assert "Hello world" in texts  # heading text (marker kept in prefix)
    assert "This is a paragraph." in texts
    assert 'print("hello")' not in texts  # code block skipped
    assert "item one" in texts

    translations = {s.index: "[FR]" + s.text for s in result.segments}
    out = tmp_path / "out.md"
    fmt.reconstruct(f, translations, result.structure, out)
    content = out.read_text(encoding="utf-8")
    assert "# [FR]Hello world" in content
    assert 'print("hello")' in content  # code intact
    assert "```python" in content
    assert "- [FR]item one" in content
    assert "> [FR]A quote here" in content
