from typing import Optional

from pydantic import BaseModel


class TaskOut(BaseModel):
    task_id: str
    filename: str
    file_type: str
    source_lang: Optional[str] = None
    detected_lang: Optional[str] = None
    target_lang: str
    engine_used: Optional[str] = None
    engine_mode: str = "local"
    status: str
    segments_total: int = 0
    segments_processed: int = 0
    errors: Optional[str] = None
    warnings: Optional[str] = None
    result_path: Optional[str] = None
    correction_enabled: bool = False
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class ProgressOut(BaseModel):
    task_id: str
    status: str
    done: int = 0
    total: int = 0
    message: str = ""
    percent: float = 0.0


class UploadResponse(BaseModel):
    task_id: str
    filename: str
    file_type: str
    detected_lang: Optional[str] = None
    engine_mode: str = "local"
    segments: int = 0


class GlossaryIn(BaseModel):
    source_term: str
    target_term: str
    context: Optional[str] = None
    domain: Optional[str] = None


class ProtectedTermIn(BaseModel):
    term: str
    category: Optional[str] = "custom"


class SettingsIn(BaseModel):
    default_target_lang: Optional[str] = None
    preferred_engine: Optional[str] = None
    local_engine: Optional[str] = None
    remote_enabled: Optional[bool] = None
    remote_endpoint: Optional[str] = None
    remote_api_key: Optional[str] = None
    correction_enabled: Optional[bool] = None
    ocr_enabled: Optional[bool] = None
    allow_auto_download: Optional[bool] = None
