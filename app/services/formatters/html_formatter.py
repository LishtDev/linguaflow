import re
from pathlib import Path
from typing import Dict, List

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter

TOKEN_RE = re.compile(
    r"(<!--.*?-->|<!\[CDATA\[.*?\]\]>|<!DOCTYPE[^>]*>|<\?.*?\?>|</?[a-zA-Z][^>]*>)",
    re.DOTALL,
)
TAG_NAME_RE = re.compile(r"</?\s*([a-zA-Z0-9]+)")
TRANSLATABLE_ATTRS = {"title", "alt", "placeholder", "aria-label", "aria-placeholder"}
CONDITIONAL_ATTRS = {"value", "label"}
ATTR_RE = re.compile(
    r"""([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))"""
)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}


def iter_attrs(tag: str):
    for m in ATTR_RE.finditer(tag):
        attr = m.group(1)
        if m.group(3) is not None:
            yield attr, '"', m.group(3)
        elif m.group(4) is not None:
            yield attr, "'", m.group(4)
        else:
            yield attr, "", m.group(5)


def extract_tokens(content: str, start_index: int, ref_tag: str = ""):
    """Return (segments, tokens) for an HTML/XHTML string.

    Segment indices start at ``start_index``. ``ref_tag`` namespaces the refs so
    multiple documents (e.g. EPUB chapters) stay distinguishable.
    """
    tokens = TOKEN_RE.split(content)
    segments: List[Segment] = []
    idx = start_index
    skip_depth = 0
    for ti, token in enumerate(tokens):
        if token.startswith("<") and not token.startswith("<!--") \
                and not token.startswith("<!"):
            name_m = TAG_NAME_RE.match(token)
            name = name_m.group(1).lower() if name_m else ""
            is_close = token.startswith("</")
            if name in ("script", "style"):
                if is_close:
                    skip_depth = max(0, skip_depth - 1)
                elif not token.rstrip().endswith("/>"):
                    skip_depth += 1
            if not is_close and not token.startswith("<!"):
                for attr, quote, value in iter_attrs(token):
                    low = attr.lower()
                    translatable = low in TRANSLATABLE_ATTRS or (
                        low in CONDITIONAL_ATTRS and name in ("input", "button", "option")
                    )
                    if translatable and value.strip():
                        segments.append(Segment(
                            index=idx, text=value,
                            ref=(ref_tag, "attr", ti, attr, quote)))
                        idx += 1
            continue
        if skip_depth == 0 and token.strip() and not token.startswith("<"):
            segments.append(Segment(
                index=idx, text=token, ref=(ref_tag, "text", ti)))
            idx += 1
    return segments, tokens


def reconstruct_tokens(tokens: List[str], segments: List[Segment],
                       translations: Dict[int, str]) -> str:
    toks = list(tokens)
    for seg in segments:
        tr = translations.get(seg.index)
        if tr is None:
            continue
        ref = seg.ref
        if ref[1] == "text":
            toks[ref[2]] = tr
        elif ref[1] == "attr":
            _, _, ti, attr, quote = ref
            toks[ti] = replace_attr(toks[ti], attr, quote, tr)
    return "".join(toks)


def replace_attr(tag: str, attr: str, quote: str, value: str) -> str:
    value = value.replace(quote, "") if quote else value.replace('"', "")
    if quote:
        pattern = re.compile(
            re.escape(attr) + r"\s*=\s*" + re.escape(quote)
            + r"[^" + re.escape(quote) + r"]*" + re.escape(quote),
            re.IGNORECASE,
        )
        return pattern.sub(f'{attr}={quote}{value}{quote}', tag, count=1)
    pattern = re.compile(re.escape(attr) + r"\s*=\s*([^\s>]+)", re.IGNORECASE)
    return pattern.sub(f'{attr}="{value}"', tag, count=1)


class HtmlFormatter(BaseFormatter):
    """HTML: translate visible text and user-facing attributes only.

    Never executes or renders scripts/styles; preserves tags exactly.
    """

    extensions = (".html", ".htm")

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        content, encoding = self.read_text(file_path)
        segments, tokens = extract_tokens(content, 0, ref_tag="html")
        return ExtractionResult(
            segments=segments,
            structure={"tokens": tokens, "encoding": encoding, "segments": segments},
        )

    def reconstruct(self, original_path, translations, structure, output_path):
        result = reconstruct_tokens(structure["tokens"], structure["segments"], translations)
        output_path.write_text(result, encoding=structure.get("encoding", "utf-8"))
        return output_path
