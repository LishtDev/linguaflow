from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.task import GlossaryIn, ProtectedTermIn
from app.services.glossary_service import GlossaryService

router = APIRouter(prefix="/api", tags=["glossary"])


@router.get("/glossary")
async def list_glossary(db: Session = Depends(get_db)):
    return [
        {"id": e.id, "source_term": e.source_term, "target_term": e.target_term,
         "context": e.context, "domain": e.domain}
        for e in GlossaryService(db).list_entries()
    ]


@router.post("/glossary")
async def add_glossary(payload: GlossaryIn, db: Session = Depends(get_db)):
    entry = GlossaryService(db).add_entry(
        payload.source_term, payload.target_term,
        payload.context or "", payload.domain or "")
    return {"id": entry.id, "source_term": entry.source_term,
            "target_term": entry.target_term}


@router.delete("/glossary/{entry_id}")
async def delete_glossary(entry_id: int, db: Session = Depends(get_db)):
    GlossaryService(db).remove_entry(entry_id)
    return {"deleted": entry_id}


@router.get("/protected-terms")
async def list_protected(db: Session = Depends(get_db)):
    return [{"id": t.id, "term": t.term, "category": t.category}
            for t in GlossaryService(db).list_protected_rows()]


@router.post("/protected-terms")
async def add_protected(payload: ProtectedTermIn, db: Session = Depends(get_db)):
    entry = GlossaryService(db).add_protected(payload.term, payload.category or "custom")
    return {"id": entry.id, "term": entry.term, "category": entry.category}


@router.delete("/protected-terms/{term_id}")
async def delete_protected(term_id: int, db: Session = Depends(get_db)):
    GlossaryService(db).remove_protected(term_id)
    return {"deleted": term_id}
