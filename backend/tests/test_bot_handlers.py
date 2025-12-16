from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

import bot.main as m


@dataclass
class _FromUser:
    id: int


class _FakeMessage:
    def __init__(self, from_user: _FromUser | None) -> None:
        self.from_user = from_user
        self.answers: list[tuple[str, Any]] = []

    async def answer(self, text: str, reply_markup: Any = None) -> None:
        self.answers.append((text, reply_markup))


def test_menu_keyboard_builds() -> None:
    kb = m._menu_kb()
    assert kb.keyboard


def test_start_cmd_ignores_messages_without_user(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fail(_: int) -> None:
        raise AssertionError("should not be called")

    class _DummyClient:
        def __init__(self, base_url: str) -> None:
            self.base_url = base_url

        ensure_user = _fail

    monkeypatch.setattr(m, "BackendClient", _DummyClient)
    monkeypatch.setattr(m, "get_settings", lambda: {"BACKEND_BASE_URL": "x", "BOT_TOKEN": "t"})

    msg = _FakeMessage(from_user=None)
    asyncio.run(m.start_cmd(msg))
    assert msg.answers == []


def test_list_tasks_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyClient:
        def __init__(self, base_url: str) -> None:
            self.base_url = base_url

        async def list_tasks(self, telegram_id: int) -> list[Any]:
            assert telegram_id == 1
            return []

    monkeypatch.setattr(m, "BackendClient", _DummyClient)
    monkeypatch.setattr(m, "get_settings", lambda: {"BACKEND_BASE_URL": "x", "BOT_TOKEN": "t"})

    msg = _FakeMessage(from_user=_FromUser(id=1))
    asyncio.run(m.list_tasks(msg))

    assert msg.answers and msg.answers[0][0] == "Задач нет."
