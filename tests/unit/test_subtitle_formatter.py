from app.services.formatters.subtitle_formatter import SubtitleFormatter


SRT = """1
00:00:01,000 --> 00:00:04,000
Hello world

2
00:00:05,000 --> 00:00:08,000
Second line
"""


def test_srt_extract_preserves_timestamps(tmp_path):
    f = tmp_path / "sub.srt"
    f.write_text(SRT, encoding="utf-8")
    fmt = SubtitleFormatter()
    result = fmt.extract(f)
    assert len(result.segments) == 2
    assert result.segments[0].text == "Hello world"
    # Timestamp lines are preserved in structure.
    assert "00:00:01,000 --> 00:00:04,000" in "\n".join(result.structure["lines"])


def test_srt_reconstruct_keeps_timestamps(tmp_path):
    f = tmp_path / "sub.srt"
    f.write_text(SRT, encoding="utf-8")
    fmt = SubtitleFormatter()
    result = fmt.extract(f)
    translations = {s.index: "Bonjour le monde" if s.index == 0 else "Deuxieme ligne"
                    for s in result.segments}
    out = tmp_path / "out.srt"
    fmt.reconstruct(f, translations, result.structure, out)
    content = out.read_text(encoding="utf-8")
    assert "00:00:01,000 --> 00:00:04,000" in content
    assert "00:00:05,000 --> 00:00:08,000" in content
    assert "Bonjour le monde" in content
    assert "1" in content and "2" in content  # cue indices


def test_srt_reading_speed_warning(tmp_path):
    f = tmp_path / "fast.srt"
    f.write_text("1\n00:00:01,000 --> 00:00:01,500\n" + "x" * 100 + "\n",
                 encoding="utf-8")
    result = SubtitleFormatter().extract(f)
    assert any("rapide" in w.lower() for w in result.warnings)


VTT = """WEBVTT

00:00:01.000 --> 00:00:04.000
Hello world
"""


def test_vtt_parsing(tmp_path):
    f = tmp_path / "sub.vtt"
    f.write_text(VTT, encoding="utf-8")
    result = SubtitleFormatter().extract(f)
    assert len(result.segments) == 1
    assert result.segments[0].text == "Hello world"
