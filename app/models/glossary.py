from sqlalchemy import Column, Integer, String, DateTime
from app.models._time import utcnow

from app.models.base import Base


class GlossaryEntry(Base):
    __tablename__ = "glossary_entries"

    id = Column(Integer, primary_key=True)
    source_term = Column(String, index=True, nullable=False)
    target_term = Column(String, nullable=False)
    context = Column(String)
    domain = Column(String)
    case_sensitive = Column(Integer, default=1)
    created_at = Column(DateTime, default=utcnow)


class ProtectedTerm(Base):
    """Terms that must always be preserved verbatim (never translated)."""
    __tablename__ = "protected_terms"

    id = Column(Integer, primary_key=True)
    term = Column(String, index=True, nullable=False)
    category = Column(String, default="custom")
    created_at = Column(DateTime, default=utcnow)
