from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class DateParseResult:
    value: datetime | None
    error: str | None


def parse_user_datetime(text: str) -> DateParseResult:
    """Args: text. Returns: parsed datetime in UTC or None."""
    raw = text.strip()
    if not raw or raw == "-":
        return DateParseResult(value=None, error=None)

    tz = ZoneInfo("America/Adak")

    try:
        dt = datetime.fromisoformat(raw) if "T" in raw else datetime.strptime(raw, "%Y-%m-%d %H:%M")
    except ValueError:
        return DateParseResult(value=None, error="Неверный формат. Используй YYYY-MM-DD HH:MM или ISO8601")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)

    return DateParseResult(value=dt.astimezone(ZoneInfo("UTC")), error=None)
