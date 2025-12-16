from __future__ import annotations

from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone

from backend.apps.notifications import tasks as notif_tasks
from backend.apps.todo.models import Task, TaskStatus
from backend.apps.users.models import User


@pytest.mark.django_db(transaction=True)
def test_send_due_notifications_marks_notified(monkeypatch: pytest.MonkeyPatch, user_profile: User) -> None:
    """Args: monkeypatch, user_profile. Returns: None."""
    sent: list[tuple[int, str]] = []

    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "test-token")

    def fake_send(tg: int, text: str) -> None:
        sent.append((tg, text))

    monkeypatch.setattr(notif_tasks, "_send_telegram_message", fake_send)

    due = timezone.now() - timedelta(minutes=1)
    task = Task.objects.create(owner=user_profile, title="due", due_at=due, status=TaskStatus.OPEN)

    count = notif_tasks.send_due_notifications()
    assert count == 1

    task.refresh_from_db()
    assert task.notified_at is not None
    assert sent and sent[0][0] == user_profile.telegram_id

    count2 = notif_tasks.send_due_notifications()
    assert count2 == 0
