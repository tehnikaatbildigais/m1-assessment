"""Pašreizējais laiks (UTC). Testos to var aizstāt, piemēram, ar monkeypatch."""

from datetime import datetime, timezone


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)
