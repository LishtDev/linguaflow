"""Timezone-aware UTC helper to avoid the deprecated datetime.utcnow()."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
