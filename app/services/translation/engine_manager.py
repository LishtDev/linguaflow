from typing import Dict, List, Optional

from app.core.exceptions import EngineUnavailableError, RemoteEngineDisabledError
from app.interfaces.translator import TranslatorInterface
from app.services.config_service import config_service
from app.services.translation.argos_translator import ArgosTranslator
from app.services.translation.remote_translator import LibreTranslateTranslator


class EngineManager:
    """Central registry + selection policy for translation engines.

    Guarantees:
      * the local engine is the default,
      * a remote engine is only usable when enabled in config AND the caller
        passes explicit consent,
      * a single engine is used for an entire document (traceability).
    """

    def _build_remote(self) -> LibreTranslateTranslator:
        return LibreTranslateTranslator(
            endpoint=config_service.get("remote_endpoint", ""),
            api_key=config_service.get("remote_api_key", ""),
            enabled=config_service.get("remote_enabled", False),
        )

    def _by_name(self, name: str) -> TranslatorInterface:
        name = (name or "").lower()
        if name in ("argos", "local"):
            return ArgosTranslator()
        if name in ("libretranslate", "remote", "distant"):
            return self._build_remote()
        raise EngineUnavailableError(f"Moteur inconnu : {name}")

    def list_engines(self) -> List[Dict]:
        engines = {
            "argos": ArgosTranslator(),
            "libretranslate": self._build_remote(),
        }
        out = []
        for key, engine in engines.items():
            remote = engine.mode == "remote"
            available = False
            try:
                available = engine.is_available()
            except Exception:
                available = False
            out.append({
                "id": key,
                "name": engine.name,
                "mode": engine.mode,
                "available": available,
                "enabled": (not remote) or config_service.get("remote_enabled", False),
                "requires_consent": remote,
                "description": self._describe(key, remote),
                "languages": self._safe_languages(engine),
            })
        return out

    @staticmethod
    def _safe_languages(engine: TranslatorInterface) -> List[str]:
        try:
            return engine.get_supported_languages()
        except Exception:
            return []

    @staticmethod
    def _describe(key: str, remote: bool) -> str:
        if key == "argos":
            return "Moteur neuronal local (hors ligne). Recommandé pour la confidentialité."
        if remote:
            return ("Moteur distant optionnel (compatible LibreTranslate). "
                    "Nécessite un consentement explicite et une configuration manuelle.")
        return key

    def select(self, requested: Optional[str] = None, consent: bool = False,
               source_lang: Optional[str] = None,
               target_lang: str = "fr") -> TranslatorInterface:
        if requested:
            engine = self._by_name(requested)
            if engine.mode == "remote":
                if not config_service.get("remote_enabled"):
                    raise RemoteEngineDisabledError(
                        "Le moteur distant est désactivé dans les paramètres."
                    )
                if not consent:
                    raise RemoteEngineDisabledError(
                        "Consentement explicite requis pour utiliser un moteur distant."
                    )
                if not engine.is_available():
                    raise EngineUnavailableError(
                        "Le moteur distant n'est pas configuré (URL manquante)."
                    )
            else:
                if not engine.is_available():
                    raise EngineUnavailableError(
                        "Aucun paquet de langue local installé pour Argos Translate. "
                        "Installez un paquet (ex. anglais -> français) dans les paramètres."
                    )
            return engine

        # Automatic selection: local first.
        local = ArgosTranslator()
        if local.is_available():
            return local

        remote = self._build_remote()
        if config_service.get("remote_enabled") and consent and remote.is_available():
            return remote

        raise EngineUnavailableError(
            "Aucun moteur de traduction disponible. Installez un paquet de langue "
            "local (Argos Translate) ou configurez un moteur distant."
        )


engine_manager = EngineManager()
