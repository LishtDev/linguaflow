from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.glossary import GlossaryEntry, ProtectedTerm


class GlossaryService:
    """Manages the user glossary and globally protected terms."""

    def __init__(self, db: Session):
        self.db = db

    # --- Glossary entries -------------------------------------------------
    def list_entries(self) -> List[GlossaryEntry]:
        return self.db.query(GlossaryEntry).order_by(GlossaryEntry.source_term).all()

    def add_entry(self, source: str, target: str, context: str = "",
                  domain: str = "") -> GlossaryEntry:
        entry = GlossaryEntry(source_term=source, target_term=target,
                              context=context or None, domain=domain or None)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete_entry(self, entry_id: int) -> bool:
        entry = self.db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_id).first()
        if not entry:
            return False
        self.db.delete(entry)
        self.db.commit()
        return True

    def as_dict(self) -> Dict[str, str]:
        return {e.source_term: e.target_term for e in self.list_entries()}

    # --- Protected terms --------------------------------------------------
    def list_protected(self) -> List[ProtectedTerm]:
        return self.db.query(ProtectedTerm).order_by(ProtectedTerm.term).all()

    def add_protected(self, term: str, category: str = "custom") -> ProtectedTerm:
        existing = self.db.query(ProtectedTerm).filter_by(term=term).first()
        if existing:
            return existing
        entry = ProtectedTerm(term=term, category=category)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def remove_entry(self, entry_id: int) -> None:
        entry = self.db.get(GlossaryEntry, entry_id)
        if entry:
            self.db.delete(entry)
            self.db.commit()

    def list_protected_rows(self) -> List[ProtectedTerm]:
        return self.db.query(ProtectedTerm).order_by(ProtectedTerm.term).all()

    def remove_protected(self, term_id: int) -> None:
        entry = self.db.get(ProtectedTerm, term_id)
        if entry:
            self.db.delete(entry)
            self.db.commit()

    def protected_terms(self) -> List[str]:
        return [t.term for t in self.db.query(ProtectedTerm).all()]
