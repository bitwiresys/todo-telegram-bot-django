from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx


@dataclass(frozen=True)
class TaskOut:
    id: str
    title: str
    description: str
    status: str
    category_name: str | None
    created_at: str
    due_at: str | None


@dataclass(frozen=True)
class CategoryOut:
    id: str
    name: str


class BackendClient:
    def __init__(self, base_url: str) -> None:
        """Args: base_url. Returns: None."""
        self._base_url = base_url.rstrip("/")

    def _headers(self, telegram_id: int) -> dict[str, str]:
        """Args: telegram_id. Returns: request headers."""
        return {
            "X-Telegram-Id": str(telegram_id),
            "Content-Type": "application/json",
        }

    async def ensure_user(self, telegram_id: int) -> None:
        """Args: telegram_id. Returns: None."""
        url = f"{self._base_url}/api/users/ensure/"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=self._headers(telegram_id))
            resp.raise_for_status()

    async def list_categories(self, telegram_id: int) -> list[CategoryOut]:
        """Args: telegram_id. Returns: categories."""
        url = f"{self._base_url}/api/categories/"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=self._headers(telegram_id))
            resp.raise_for_status()
            data = resp.json()

        if not isinstance(data, list):
            raise ValueError("Unexpected categories response")

        out: list[CategoryOut] = []
        for item in data:
            out.append(CategoryOut(id=str(item["id"]), name=str(item["name"])))
        return out

    async def list_tasks(self, telegram_id: int) -> list[TaskOut]:
        """Args: telegram_id. Returns: tasks."""
        url = f"{self._base_url}/api/tasks/"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=self._headers(telegram_id))
            resp.raise_for_status()
            data = resp.json()

        if not isinstance(data, list):
            raise ValueError("Unexpected tasks response")

        out: list[TaskOut] = []
        for item in data:
            out.append(
                TaskOut(
                    id=str(item["id"]),
                    title=str(item["title"]),
                    description=str(item.get("description") or ""),
                    status=str(item["status"]),
                    category_name=(str(item["category_name"]) if item.get("category_name") else None),
                    created_at=str(item["created_at"]),
                    due_at=(str(item["due_at"]) if item.get("due_at") else None),
                )
            )
        return out

    async def create_task(
        self,
        telegram_id: int,
        title: str,
        description: str,
        category_id: str | None,
        due_at_utc: datetime | None,
    ) -> TaskOut:
        """Args: telegram_id, title, description, category_id, due_at_utc. Returns: created task."""
        url = f"{self._base_url}/api/tasks/"

        payload: dict[str, Any] = {
            "title": title,
            "description": description,
            "category": category_id,
        }
        if due_at_utc is not None:
            payload["due_at"] = due_at_utc.astimezone(timezone.utc).isoformat()

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=self._headers(telegram_id), json=payload)
            resp.raise_for_status()
            item = resp.json()

        return TaskOut(
            id=str(item["id"]),
            title=str(item["title"]),
            description=str(item.get("description") or ""),
            status=str(item["status"]),
            category_name=(str(item["category_name"]) if item.get("category_name") else None),
            created_at=str(item["created_at"]),
            due_at=(str(item["due_at"]) if item.get("due_at") else None),
        )
