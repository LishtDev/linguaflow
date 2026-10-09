from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "LinguaFlow"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Server - bound to localhost only by default for security
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/linguaflow.db"

    # Storage paths
    DATA_DIR: Path = BASE_DIR / "data"
    TEMP_DIR: Path = BASE_DIR / "data" / "temp"
    RESULTS_DIR: Path = BASE_DIR / "data" / "results"
    MODELS_DIR: Path = BASE_DIR / "data" / "models"
    CACHE_DIR: Path = BASE_DIR / "data" / "cache"

    # Translation
    DEFAULT_TARGET_LANG: str = "fr"
    LOCAL_ENGINE: str = "argos"
    REMOTE_ENGINES_ENABLED: bool = False
    ALLOW_AUTO_DOWNLOAD: bool = False

    # Files
    MAX_FILE_SIZE_MB: int = 50
    MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024

    # Processing
    MAX_PROCESSING_SECONDS: int = 1800
    SEGMENT_CHAR_LIMIT: int = 1500
    JOBS_MAX_WORKERS: int = 2

    # OCR
    TESSERACT_LANG: str = "fra+eng"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def allowed_extensions(self) -> set:
        return {
            "txt", "md", "html", "htm", "csv",
            "docx", "doc", "pptx", "xlsx",
            "pdf", "epub", "srt", "vtt",
            "jpg", "jpeg", "png", "tif", "tiff", "bmp",
        }


settings = Settings()

for _d in (settings.DATA_DIR, settings.TEMP_DIR, settings.RESULTS_DIR,
           settings.MODELS_DIR, settings.CACHE_DIR):
    _d.mkdir(parents=True, exist_ok=True)
