from abc import ABC, abstractmethod
from typing import List, Optional


class TranslatorInterface(ABC):
    """Common contract for every translation engine (local or remote)."""

    name: str = "unknown"
    mode: str = "local"  # "local" | "remote"

    @abstractmethod
    def translate(self, text: str, source_lang: Optional[str], target_lang: str) -> str:
        """Translate a single segment. Must never raise on benign input;
        callers rely on a conservative return of the source text on failure."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        raise NotImplementedError

    def supports_pair(self, source_lang: str, target_lang: str) -> bool:
        return True

    def detect(self, text: str) -> Optional[str]:
        return None
