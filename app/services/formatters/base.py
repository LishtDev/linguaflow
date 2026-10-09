from pathlib import Path

from app.interfaces.formatter import FormatterInterface


class BaseFormatter(FormatterInterface):
    """Helpers shared by concrete formatters."""

    ext_map = {}

    @staticmethod
    def read_text(path: Path) -> tuple:
        """Read text honoring BOM/encoding. Returns (text, encoding).

        The BOM is only kept as ``utf-8-sig`` when actually present, so that
        writing back with the returned encoding is symmetric.
        """
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            try:
                return raw.decode("utf-8-sig"), "utf-8-sig"
            except UnicodeDecodeError:
                pass
        for enc in ("utf-8", "latin-1"):
            try:
                return raw.decode(enc), enc
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace"), "utf-8"

    @classmethod
    def detect_encoding(cls, path: Path) -> str:
        _, enc = cls.read_text(path)
        return enc
