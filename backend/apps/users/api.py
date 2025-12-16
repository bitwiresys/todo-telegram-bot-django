from __future__ import annotations

from django.db import transaction
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.users.models import User


class EnsureUserView(APIView):
    authentication_classes: list[type[BaseAuthentication]] = []
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Args: request. Returns: response with ensured user."""
        telegram_id_raw = request.headers.get("X-Telegram-Id")
        if not telegram_id_raw:
            return Response({"detail": "Missing X-Telegram-Id"}, status=400)

        try:
            telegram_id = int(telegram_id_raw)
        except ValueError:
            return Response({"detail": "Invalid X-Telegram-Id"}, status=400)

        with transaction.atomic():
            user = User.objects.filter(telegram_id=telegram_id).first()
            if user is not None:
                return Response({"id": user.id, "telegram_id": user.telegram_id})

            user = User.objects.create_user(telegram_id=telegram_id)

        return Response({"id": user.id, "telegram_id": user.telegram_id}, status=201)
