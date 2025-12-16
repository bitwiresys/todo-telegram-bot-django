from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, cast

import pytest

import bot.dialogs.add_task as m


@dataclass
class _FromUser:
    id: int


class _Event:
    def __init__(self, from_user: _FromUser | None) -> None:
        self.from_user = from_user


class _DialogManager:
    def __init__(self, from_user: _FromUser | None) -> None:
        self.event = _Event(from_user)
        self.dialog_data: dict[str, Any] = {}
        self.done_called = False

    async def done(self) -> None:
        self.done_called = True


class _DummyClient:
    def __init__(self) -> None:
        self.created: list[dict[str, Any]] = []

    async def list_categories(self, telegram_id: int) -> list[Any]:
        return [type("C", (), {"id": "cat_1", "name": "work"})()]

    async def create_task(
        self,
        telegram_id: int,
        title: str,
        description: str,
        category_id: str | None,
        due_at_utc: datetime | None,
    ) -> Any:
        self.created.append(
            {
                "telegram_id": telegram_id,
                "title": title,
                "description": description,
                "category_id": category_id,
                "due_at": due_at_utc,
            }
        )
        return type(
            "T",
            (),
            {
                "title": title,
                "category_name": "work",
                "created_at": "now",
                "due_at": "-",
            },
        )()


def test_get_categories_returns_empty_without_user() -> None:
    dm = _DialogManager(from_user=None)
    out = asyncio.run(m._get_categories(cast(Any, dm)))
    assert out == {"categories": []}


def test_confirm_data_formats_category_and_due(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy = _DummyClient()
    monkeypatch.setattr(m, "_client", lambda: dummy)

    dm = _DialogManager(from_user=_FromUser(id=1))
    dm.dialog_data["title"] = "t"
    dm.dialog_data["description"] = "d"
    dm.dialog_data["category_id"] = "cat_1"
    dm.dialog_data["due_at"] = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)

    data = asyncio.run(m._confirm_data(cast(Any, dm)))
    assert data["category_name"] == "work"
    assert data["due"] != "-"


def test_on_create_ignores_without_user(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy = _DummyClient()
    monkeypatch.setattr(m, "_client", lambda: dummy)

    cb = type("CB", (), {"from_user": None, "message": object()})()
    dm = _DialogManager(from_user=_FromUser(id=1))

    asyncio.run(m._on_create(cast(Any, cb), cast(Any, object()), cast(Any, dm)))
    assert dummy.created == []


def test_on_create_calls_client_and_done(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy = _DummyClient()
    monkeypatch.setattr(m, "_client", lambda: dummy)

    cb = type("CB", (), {"from_user": _FromUser(id=5), "message": object()})()
    dm = _DialogManager(from_user=_FromUser(id=5))
    dm.dialog_data.update({"title": "t", "description": "d", "category_id": None, "due_at": None})

    asyncio.run(m._on_create(cast(Any, cb), cast(Any, object()), cast(Any, dm)))
    assert dummy.created and dm.done_called
