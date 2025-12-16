from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from backend.apps.users.models import User


@pytest.fixture()
def api_client() -> APIClient:
    """Args: none. Returns: DRF API client."""
    return APIClient()


@pytest.fixture()
def user_profile(db: object) -> User:
    """Args: db. Returns: created User."""
    return User.objects.create_user(telegram_id=111)


@pytest.fixture()
def other_profile(db: object) -> User:
    """Args: db. Returns: created User."""
    return User.objects.create_user(telegram_id=222)


def auth_headers(telegram_id: int) -> dict[str, str]:
    """Args: telegram_id. Returns: auth headers."""
    return {"HTTP_X_TELEGRAM_ID": str(telegram_id)}
