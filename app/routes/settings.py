from fastapi import APIRouter, HTTPException

from app.schemas.task import SettingsIn
from app.services.config_service import config_service
from app.services.translation.engine_manager import engine_manager

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/engines")
async def list_engines():
    return {
        "engines": engine_manager.list_engines(),
        "local_default": "argos",
        "remote_enabled": config_service.get("remote_enabled", False),
    }


@router.get("/settings")
async def get_settings():
    return config_service.public()


@router.put("/settings")
async def update_settings(payload: SettingsIn):
    values = {k: v for k, v in payload.model_dump().items() if v is not None}
    # Refuse to silently enable a remote engine without an endpoint.
    if values.get("remote_enabled"):
        endpoint = values.get("remote_endpoint", config_service.get("remote_endpoint", ""))
        if not endpoint:
            raise HTTPException(
                400, "Un moteur distant nécessite une URL de service."
            )
    config_service.update(values)
    return config_service.public()


@router.post("/settings/remote-consent")
async def set_remote_consent(consent: bool):
    config_service.update({"remote_consent": bool(consent)})
    return {"remote_consent": bool(consent)}


@router.get("/languages")
async def languages():
    from app.services.language_detector import LANGUAGE_NAMES_FR
    installed = []
    try:
        from app.services.translation.argos_translator import ArgosTranslator
        installed = ArgosTranslator().get_supported_languages()
    except Exception:
        installed = []
    return {"all": LANGUAGE_NAMES_FR, "installed_local": installed}
