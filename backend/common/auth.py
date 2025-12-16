from __future__ import annotations

from dataclasses import dataclass

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from backend.apps.users.models import User


@dataclass(frozen=True)
class AuthContext:
    user: User


class TelegramIdAuthentication(BaseAuthentication):
    def authenticate(self, request: Request) -> tuple[User, AuthContext] | None:
        """Args: request. Returns: (user, auth_context) or None."""
        telegram_id_raw = request.headers.get("X-Telegram-Id")
        if not telegram_id_raw:
            raise AuthenticationFailed("Missing X-Telegram-Id")

        try:
            telegram_id = int(telegram_id_raw)
        except ValueError as exc:
            raise AuthenticationFailed("Invalid X-Telegram-Id") from exc

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("Unknown user") from exc

        return (user, AuthContext(user=user))
