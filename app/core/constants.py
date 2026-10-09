# Engine types
ENGINE_LOCAL = "local"
ENGINE_REMOTE = "remote"

# Task states
TASK_PENDING = "pending"
TASK_IN_PROGRESS = "in_progress"
TASK_INTERRUPTED = "interrupted"
TASK_COMPLETED = "completed"
TASK_FAILED = "failed"

VALID_TASK_STATES = {
    TASK_PENDING, TASK_IN_PROGRESS, TASK_INTERRUPTED,
    TASK_COMPLETED, TASK_FAILED,
}

# File categories
FILE_TYPE_TEXT = "text"
FILE_TYPE_OFFICE = "office"
FILE_TYPE_PDF = "pdf"
FILE_TYPE_EPUB = "epub"
FILE_TYPE_SUBTITLE = "subtitle"
FILE_TYPE_IMAGE = "image"

FORMAT_CATEGORIES = {
    "txt": FILE_TYPE_TEXT,
    "md": FILE_TYPE_TEXT,
    "html": FILE_TYPE_TEXT,
    "htm": FILE_TYPE_TEXT,
    "csv": FILE_TYPE_TEXT,
    "docx": FILE_TYPE_OFFICE,
    "doc": FILE_TYPE_OFFICE,
    "pptx": FILE_TYPE_OFFICE,
    "xlsx": FILE_TYPE_OFFICE,
    "pdf": FILE_TYPE_PDF,
    "epub": FILE_TYPE_EPUB,
    "srt": FILE_TYPE_SUBTITLE,
    "vtt": FILE_TYPE_SUBTITLE,
    "jpg": FILE_TYPE_IMAGE,
    "jpeg": FILE_TYPE_IMAGE,
    "png": FILE_TYPE_IMAGE,
    "tif": FILE_TYPE_IMAGE,
    "tiff": FILE_TYPE_IMAGE,
    "bmp": FILE_TYPE_IMAGE,
}
