from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.core.exceptions import LinguaFlowError
from app.core.logging_config import logger
from app.core.templating import STATIC_DIR
from app.models import Base  # noqa: F401
from app.routes import glossary, history, main, settings as settings_routes, tasks, upload
from app.services.task_service import TaskService


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        TaskService(db).mark_interrupted()
    finally:
        db.close()
    logger.info("%s %s démarré sur %s:%s (mode local par défaut).",
                settings.APP_NAME, settings.VERSION, settings.HOST, settings.PORT)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Traduction documentaire locale vers le français.",
    lifespan=lifespan,
)

init_db()

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Pages
app.include_router(main.router)
# API
app.include_router(upload.router)
app.include_router(tasks.router)
app.include_router(history.router)
app.include_router(settings_routes.router)
app.include_router(glossary.router)


@app.exception_handler(LinguaFlowError)
async def linguaflow_exception_handler(request: Request, exc: LinguaFlowError):
    return JSONResponse(status_code=exc.status_code,
                        content={"detail": str(exc), "type": exc.__class__.__name__})
