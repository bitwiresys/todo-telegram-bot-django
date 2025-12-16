from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from backend.apps.todo.filters import TaskFilter
from backend.apps.todo.models import Category, Task
from backend.apps.todo.serializers import CategorySerializer, TaskSerializer
from backend.apps.users.models import User


def _get_user(request: Request) -> User:
    """Args: request. Returns: authenticated user."""
    user = request.user
    if isinstance(user, User):
        return user
    raise RuntimeError("User missing")


class CategoryViewSet(ModelViewSet[Category]):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get_queryset(self) -> QuerySet[Category]:
        """Args: none. Returns: queryset."""
        user = _get_user(self.request)
        return Category.objects.filter(owner=user).order_by("-created_at")

    def perform_create(self, serializer: Any) -> None:
        """Args: serializer. Returns: None."""
        user = _get_user(self.request)
        serializer.save(owner=user)


class TaskViewSet(ModelViewSet[Task]):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    ordering_fields = ["created_at", "due_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self) -> QuerySet[Task]:
        """Args: none. Returns: queryset."""
        user = _get_user(self.request)
        return (
            Task.objects.select_related("category")
            .filter(owner=user)
            .order_by("-created_at")
        )

    def perform_create(self, serializer: Any) -> None:
        """Args: serializer. Returns: None."""
        user = _get_user(self.request)
        category = serializer.validated_data.get("category")
        if category is not None and isinstance(category, Category) and category.owner_id != user.id:
            raise ValidationError({"category": "Invalid category"})
        serializer.save(owner=user)

    def perform_update(self, serializer: Any) -> None:
        """Args: serializer. Returns: None."""
        user = _get_user(self.request)
        category = serializer.validated_data.get("category")
        if category is not None and isinstance(category, Category) and category.owner_id != user.id:
            raise ValidationError({"category": "Invalid category"})
        serializer.save()
