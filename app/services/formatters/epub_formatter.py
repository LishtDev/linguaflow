import zipfile
from pathlib import Path
from typing import Dict, List

from app.interfaces.formatter import ExtractionResult, Segment
from app.services.formatters.base import BaseFormatter
from app.services.formatters.html_formatter import extract_tokens, reconstruct_tokens

DOC_EXTS = (".xhtml", ".html", ".htm")


class EpubFormatter(BaseFormatter):
    """EPUB (zipped XHTML): translate document items, preserve everything else.

    Implemented with ``zipfile`` so that images, CSS, fonts, OPF metadata and
    navigation are copied byte-for-byte. Only text nodes and user-facing
    attributes of XHTML entries are changed.
    """

    extensions = (".epub",)

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        segments: List[Segment] = []
        docs: Dict[str, dict] = {}
        idx = 0
        with zipfile.ZipFile(file_path, "r") as zf:
            for name in zf.namelist():
                if not name.lower().endswith(DOC_EXTS):
                    continue
                raw = zf.read(name)
                content = self._decode(raw)
                segs, tokens = extract_tokens(content, idx, ref_tag=name)
                idx += len(segs)
                docs[name] = {"tokens": tokens, "segments": segs}
                segments.extend(segs)

        return ExtractionResult(
            segments=segments,
            structure={"docs": docs},
            warnings=[],
        )

    def reconstruct(self, original_path, translations, structure, output_path):
        docs = structure.get("docs", {})
        with zipfile.ZipFile(original_path, "r") as zin:
            names = zin.namelist()
            contents = {n: zin.read(n) for n in names}
            infos = {n: zin.getinfo(n) for n in names}

        # Rewrite document entries.
        for name, doc in docs.items():
            rebuilt = reconstruct_tokens(doc["tokens"], doc["segments"], translations)
            contents[name] = rebuilt.encode("utf-8")

        # Write a new epub; mimetype must be first and stored uncompressed.
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            ordered = sorted(names, key=lambda n: (n != "mimetype", n))
            for name in ordered:
                info = infos[name]
                if name == "mimetype":
                    zout.writestr(zipfile.ZipInfo("mimetype"), contents[name],
                                  compress_type=zipfile.ZIP_STORED)
                else:
                    zout.writestr(info.filename, contents[name],
                                  compress_type=zipfile.ZIP_DEFLATED)
        return output_path

    @staticmethod
    def _decode(raw: bytes) -> str:
        for enc in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")
