import re

# Regex patterns for elements that must never be altered by translation.
# NOTE: common English words (function, class, return, ...) are intentionally
# NOT protected here, per the requirement not to protect ordinary words.
DEFAULT_PATTERNS = {
    # Code (processed first, highest priority)
    "code_block": r"```[\s\S]*?```",
    "code_inline": r"`[^`\n]+`",
    # Links / contact
    "url": r"https?://[^\s<>\"')]+",
    "www": r"\bwww\.[^\s<>\"')]+",
    "email": r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b",
    # File paths
    "path_unix": r"(?<![\w])(?:\.{1,2}/|~/)[\w./\-]+",
    "path_windows": r"\b[A-Za-z]:\\[\w\\ .\-]+",
    # Technical identifiers / versions
    "version": r"\bv?\d+\.\d+(?:\.\d+)?(?:[-.][\w]+)?\b",
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b",
    "filename": r"\b[\w\-. ]+\.(?:py|js|ts|java|c|cpp|h|go|rs|rb|php|sh|json|yaml|yml|xml|ini|conf|cfg|toml|env|sql|css|html|md)\b",
    # Code identifiers with clear markers
    "snake_case": r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b",
    "call_expr": r"\b[A-Za-z_][\w]*\(\)",
    # Excel
    "excel_formula": r"=[A-Z]+\d*(?:\([^)]*\)|[^\s,;)]*)(?:[+\-*/&^][^\s,;)]+)*",
    "excel_ref": r"\b\$?[A-Z]{1,3}\$?\d{1,7}(?::\$?[A-Z]{1,3}\$?\d{1,7})?\b",
}


class ElementProtector:
    """Reversible protection of non-translatable elements.

    Two strategies are combined for robustness:

    * Fast path: replace protected spans with ``%LFTOKEN{n}%`` tokens,
      translate the whole segment (better fluency), then restore exactly. Used
      only when every token survives translation intact.
    * Safe fallback: if any token is altered by the engine, translate the
      translatable chunks separately and re-insert the original spans
      verbatim, guaranteeing perfect preservation.

    This guarantees technical elements are never mistranslated, regardless of
    the engine's token handling.
    """

    def __init__(self, custom_protected=None, glossary=None):
        self.patterns = {name: re.compile(rx, re.MULTILINE)
                         for name, rx in DEFAULT_PATTERNS.items()}
        self.custom_protected = [t for t in (custom_protected or []) if t.strip()]
        self.glossary = glossary or {}
        self._ph_re = re.compile(r"%LFTOKEN(\d+)%")

    # -- span collection --------------------------------------------------
    def _collect_spans(self, text: str):
        """Return non-overlapping spans: (start, end, matched, type, replacement)."""
        spans = []
        claimed = []

        def overlaps(s, e):
            return any(not (e <= cs or s >= ce) for cs, ce in claimed)

        def add(start, end, matched, typ, replacement):
            claimed.append((start, end))
            spans.append((start, end, matched, typ, replacement))

        for term in sorted(self.custom_protected, key=len, reverse=True):
            for m in re.finditer(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text):
                if not overlaps(m.start(), m.end()):
                    add(m.start(), m.end(), m.group(0), "custom", m.group(0))

        for term in sorted(self.glossary.keys(), key=len, reverse=True):
            for m in re.finditer(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text):
                if not overlaps(m.start(), m.end()):
                    add(m.start(), m.end(), m.group(0), "glossary",
                        self.glossary[term])

        for name, pattern in self.patterns.items():
            for m in pattern.finditer(text):
                original = m.group(0)
                if not original.strip():
                    continue
                if self._ph_re.search(original):
                    continue
                if overlaps(m.start(), m.end()):
                    continue
                add(m.start(), m.end(), original, name, original)

        spans.sort(key=lambda x: x[0])
        return spans

    def _build(self, text, spans):
        result = []
        placeholders = []
        last = 0
        for i, (s, e, matched, typ, replacement) in enumerate(spans, 1):
            result.append(text[last:s])
            ph = f"%LFTOKEN{i}%"
            placeholders.append({
                "id": i, "placeholder": ph,
                "original": matched, "replacement": replacement, "type": typ,
            })
            result.append(ph)
            last = e
        result.append(text[last:])
        return "".join(result), placeholders

    # -- public API -------------------------------------------------------
    def protect(self, text: str):
        spans = self._collect_spans(text)
        if not spans:
            return text, []
        return self._build(text, spans)

    def restore(self, text: str, placeholders) -> str:
        restored = text
        for ph in sorted(placeholders, key=lambda p: p["id"], reverse=True):
            restored = restored.replace(ph["placeholder"],
                                        ph.get("replacement", ph["original"]))
        return restored

    def has_leftover_placeholders(self, text: str) -> bool:
        return bool(self._ph_re.search(text))

    def translate(self, engine, text: str, source_lang, target_lang: str) -> str:
        """Translate while preserving protected elements exactly."""
        if not text or not text.strip():
            return text
        spans = self._collect_spans(text)
        if not spans:
            return engine.translate(text, source_lang, target_lang)

        protected, placeholders = self._build(text, spans)
        out = engine.translate(protected, source_lang, target_lang)

        if all(ph["placeholder"] in out for ph in placeholders):
            return self.restore(out, placeholders)

        # Safe fallback: translate only the translatable chunks.
        return self._translate_by_spans(engine, text, spans, source_lang, target_lang)

    def _translate_by_spans(self, engine, text, spans, source_lang, target_lang):
        parts = []
        last = 0
        for s, e, matched, typ, replacement in spans:
            chunk = text[last:s]
            parts.append(self._translate_chunk(engine, chunk, source_lang, target_lang))
            parts.append(replacement)
            last = e
        parts.append(self._translate_chunk(engine, text[last:], source_lang, target_lang))
        return "".join(parts)

    @staticmethod
    def _translate_chunk(engine, chunk, source_lang, target_lang):
        """Translate a chunk while preserving its surrounding whitespace.

        Engines often trim leading/trailing spaces, which would glue protected
        elements to adjacent words after re-insertion.
        """
        if not chunk.strip():
            return chunk
        lead = chunk[:len(chunk) - len(chunk.lstrip())]
        trail = chunk[len(chunk.rstrip()):]
        core = chunk.strip()
        translated = engine.translate(core, source_lang, target_lang)
        return lead + translated + trail
