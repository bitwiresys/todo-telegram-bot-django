from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pytest
import httpx

from bot.api_client import BackendClient


@dataclass
class _DummyResponse:
    json_data: Any

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self.json_data


class _DummyAsyncClient:
    def __init__(self, *, timeout: float) -> None:
        self.timeout = timeout
        self.calls: list[tuple[str, str, dict[str, str], Any]] = []
        self._responses: list[_DummyResponse] = []

    async def __aenter__(self) -> _DummyAsyncClient:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def queue_response(self, resp: _DummyResponse) -> None:
        self._responses.append(resp)

    async def post(self, url: str, *, headers: dict[str, str], json: Any = None) -> _DummyResponse:
        self.calls.append(("POST", url, headers, json))
        return self._responses.pop(0)

    async def get(self, url: str, *, headers: dict[str, str]) -> _DummyResponse:
        self.calls.append(("GET", url, headers, None))
        return self._responses.pop(0)


@pytest.mark.parametrize("telegram_id", [1, 999])
def test_headers_include_telegram_id(telegram_id: int) -> None:
    c = BackendClient(base_url="http://x")
    h = c._headers(telegram_id)
    assert h["X-Telegram-Id"] == str(telegram_id)
    assert h["Content-Type"] == "application/json"


def test_ensure_user_calls_correct_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy = _DummyAsyncClient(timeout=10.0)
    dummy.queue_response(_DummyResponse(json_data=None))

    def _factory(*, timeout: float) -> _DummyAsyncClient:
        assert timeout == 10.0
        return dummy

    monkeypatch.setattr(httpx, "AsyncClient", _factory)

    c = BackendClient(base_url="http://example")
    asyncio.run(c.ensure_user(telegram_id=10))

    assert dummy.calls
    method, url, headers, payload = dummy.calls[0]
    assert method == "POST"
    assert url == "http://example/api/users/ensure/"
    assert headers["X-Telegram-Id"] == "10"
    assert payload is None


def test_create_task_serializes_due_at(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy = _DummyAsyncClient(timeout=10.0)
    dummy.queue_response(
        _DummyResponse(
            json_data={
                "id": "tsk_1",
                "title": "t",
                "description": "",
                "status": "open",
                "category_name": None,
                "created_at": "2025-01-01T00:00:00Z",
                "due_at": "2025-01-01T00:00:00+00:00",
            }
        )
    )

    monkeypatch.setattr(httpx, "AsyncClient", lambda *, timeout: dummy)

    c = BackendClient(base_url="http://example")
    due = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    out = asyncio.run(
        c.create_task(telegram_id=10, title="t", description="", category_id=None, due_at_utc=due)
    )

    assert out.id == "tsk_1"

    method, url, headers, payload = dummy.calls[0]
    assert method == "POST"
    assert url == "http://example/api/tasks/"
    assert payload["due_at"].endswith("+00:00")
