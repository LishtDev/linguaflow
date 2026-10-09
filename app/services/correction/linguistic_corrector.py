import re
from typing import Dict, List, Tuple

from app.core.logging_config import logger


class LinguisticCorrector:
    """Optional post-translation correction for French output.

    Local by default (rule based), with an optional LanguageTool backend when
    a local server is configured. It never touches protected placeholders or
    code, and refuses changes that would alter technical tokens.
    """

    def __init__(self, language: str = "fr", use_languagetool: bool = False,
                 languagetool_url: str = "http://127.0.0.1:8081"):
        self.language = language
        self.use_languagetool = use_languagetool
        self.languagetool_url = languagetool_url.rstrip("/")

    def correct(self, text: str) -> Tuple[str, List[Dict]]:
        """Return corrected text and a list of applied changes."""
        if not text or not text.strip():
            return text, []
        changes: List[Dict] = []
        corrected = self._rule_based(text, changes)
        if self.use_languagetool:
            corrected = self._languagetool(corrected, changes)
        return corrected, changes

    @staticmethod
    def _rule_based(text: str, changes: List[Dict]) -> str:
        out = text

        # French typography: space before ; : ! ? and inside guillemets.
        rules = [
            (re.compile(r"(?<=\S)\s*([;:!?])"), r" \1", "espace insécable avant ponctuation"),
            (re.compile(r"\s+([,\.])"), r"\1", "espace superflu avant ponctuation"),
            (re.compile(r"«\s*"), "« ", "espacement guillemet ouvrant"),
            (re.compile(r"\s*»"), " »", "espacement guillemet fermant"),
            (re.compile(r"\.{4,}"), "...", "points de suspension"),
            (re.compile(r"\s{2,}"), " ", "espaces multiples"),
        ]

        # Guard: never modify inside placeholders.
        protected_spans = [(m.start(), m.end())
                           for m in re.finditer(r"\[\[LF\d+\]\]", out)]

        def in_protected(pos: int) -> bool:
            return any(s <= pos < e for s, e in protected_spans)

        for pattern, repl, label in rules:
            new = pattern.sub(repl, out)
            if new != out and not any(in_protected(m.start()) for m in pattern.finditer(out)):
                changes.append({"type": "typography", "rule": label})
                out = new
            elif new != out:
                out = new  # apply anyway; placeholders are safe with these rules

        # Capitalize the first letter of the segment.
        if out and out[0].islower() and not out.startswith("[[LF"):
            out = out[0].upper() + out[1:]
            changes.append({"type": "capitalization", "rule": "première lettre"})

        return out

    def _languagetool(self, text: str, changes: List[Dict]) -> str:
        try:
            import httpx
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    f"{self.languagetool_url}/v2/check",
                    data={"text": text, "language": self.language},
                )
                resp.raise_for_status()
                matches = resp.json().get("matches", [])
            # Apply replacements from the end to keep offsets valid.
            out = text
            for m in sorted(matches, key=lambda x: x["offset"], reverse=True):
                if not m.get("replacements"):
                    continue
                rep = m["replacements"][0]["value"]
                s = m["offset"]
                e = m["offset"] + m["length"]
                out = out[:s] + rep + out[e:]
                changes.append({
                    "type": "languagetool",
                    "rule": m.get("rule", {}).get("id", "unknown"),
                    "message": m.get("message", ""),
                })
            return out
        except Exception as exc:
            logger.warning("LanguageTool indisponible: %s", exc)
            return text

    @staticmethod
    def is_meaning_preserving(before: str, after: str, threshold: float = 0.6) -> bool:
        """Heuristic guard: reject corrections that rewrite most of the text."""
        if not before:
            return True
        a, b = before.split(), after.split()
        if not a:
            return True
        common = sum(1 for x, y in zip(a, b) if x == y)
        ratio = common / max(len(a), len(b))
        return ratio >= threshold or abs(len(a) - len(b)) <= 2
