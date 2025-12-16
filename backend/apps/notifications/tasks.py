from __future__ import annotations

from typing import Any, TypeVar, cast
from collections.abc import Callable

import httpx
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from backend.apps.todo.models import Task, TaskStatus


_F = TypeVar("_F", bound=Callable[..., object])


def _typed_shared_task(func: _F) -> _F:
    return cast(_F, shared_task(func))


def _build_message(task: Task) -> str:
    """Args: task. Returns: message text."""
    due = task.due_at.isoformat() if task.due_at else "-"
    return f"Напоминание: {task.title}\nСоздано: {task.created_at.isoformat()}\nДедлайн: {due}"


def _send_telegram_message(telegram_id: int, text: str) -> None:
    """Args: telegram_id, text. Returns: None."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload: dict[str, Any] = {"chat_id": telegram_id, "text": text}

    with httpx.Client(timeout=10.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()


@_typed_shared_task
def send_due_notifications() -> int:
    """Args: none. Returns: count of notified tasks."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return 0
    now = timezone.now()

    tasks = (
        Task.objects.select_related("owner")
        .filter(
            status=TaskStatus.OPEN,
            due_at__isnull=False,
            due_at__lte=now,
            notified_at__isnull=True,
        )
        .order_by("due_at")
    )

    notified = 0

    for task in tasks:
        with transaction.atomic():
            locked = (
                Task.objects.select_for_update()
                .select_related("owner")
                .filter(id=task.id)
                .first()
            )
            if locked is None or locked.notified_at is not None:
                continue
            if locked.due_at is None or locked.due_at > now:
                continue

            _send_telegram_message(locked.owner.telegram_id, _build_message(locked))
            locked.notified_at = timezone.now()
            locked.save(update_fields=["notified_at"])
            notified += 1

    return notified
