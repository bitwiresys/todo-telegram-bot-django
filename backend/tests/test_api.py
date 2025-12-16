from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from backend.apps.todo.models import Category, Task, TaskStatus
from backend.apps.users.models import User
from backend.tests.conftest import auth_headers


@pytest.mark.django_db()
def test_ensure_user_creates_profile(api_client: APIClient) -> None:
    """Args: api_client. Returns: None."""
    api_client.credentials(**auth_headers(telegram_id=999))
    resp = api_client.post("/api/users/ensure/")
    assert resp.status_code == 201
    assert resp.json()["telegram_id"] == 999


@pytest.mark.django_db()
def test_category_crud_scoped(api_client: APIClient, user_profile: User, other_profile: User) -> None:
    """Args: api_client, user_profile, other_profile. Returns: None."""
    api_client.credentials(**auth_headers(user_profile.telegram_id))
    resp = api_client.post(
        "/api/categories/",
        data={"name": "work"},
        format="json",
    )
    assert resp.status_code == 201

    Category.objects.create(owner=other_profile, name="other")

    resp2 = api_client.get("/api/categories/")
    assert resp2.status_code == 200
    names = [c["name"] for c in resp2.json()]
    assert names == ["work"]


@pytest.mark.django_db()
def test_task_crud_and_filtering(api_client: APIClient, user_profile: User) -> None:
    """Args: api_client, user_profile. Returns: None."""
    api_client.credentials(**auth_headers(user_profile.telegram_id))
    cat = Category.objects.create(owner=user_profile, name="home")

    due = timezone.now() + timedelta(hours=1)

    resp = api_client.post(
        "/api/tasks/",
        data={"title": "t1", "description": "", "category": cat.id, "due_at": due.isoformat()},
        format="json",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["category_name"] == "home"
    assert body["created_at"]

    Task.objects.create(owner=user_profile, title="t2", status=TaskStatus.DONE)

    resp2 = api_client.get("/api/tasks/?status=done")
    assert resp2.status_code == 200
    titles = [t["title"] for t in resp2.json()]
    assert titles == ["t2"]
