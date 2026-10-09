from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.templating import templates
from app.services.formatters.registry import registry
from app.services.translation.engine_manager import engine_manager

router = APIRouter(tags=["pages"])


def render(request, name, context=None):
    """Starlette-compatible page renderer (new request-first signature)."""
    return templates.TemplateResponse(request, name, context or {})


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render(request, "index.html", {
        "formats": registry.supported_extensions(),
        "engines": engine_manager.list_engines(),
    })


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return render(request, "history.html")


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return render(request, "settings.html", {
        "engines": engine_manager.list_engines(),
    })


@router.get("/glossary", response_class=HTMLResponse)
async def glossary_page(request: Request):
    return render(request, "glossary.html")


@router.get("/tasks/{task_id}", response_class=HTMLResponse)
async def task_page(request: Request, task_id: str):
    return render(request, "task_detail.html", {"task_id": task_id})


@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0", "mode": "local-first"}
