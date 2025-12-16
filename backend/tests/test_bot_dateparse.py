from __future__ import annotations

from bot.dateparse import parse_user_datetime


def test_parse_user_datetime_skip() -> None:
    """Args: none. Returns: None."""
    res = parse_user_datetime("-")
    assert res.error is None
    assert res.value is None


def test_parse_user_datetime_invalid() -> None:
    """Args: none. Returns: None."""
    res = parse_user_datetime("nope")
    assert res.value is None
    assert res.error
