from __future__ import annotations

from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from backend.apps.todo.models import Category, Task


class CategorySerializer(serializers.ModelSerializer[Category]):
    class Meta:
        model = Category
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class TaskSerializer(serializers.ModelSerializer[Task]):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "due_at",
            "status",
            "category",
            "category_name",
            "created_at",
            "updated_at",
            "notified_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "notified_at", "category_name"]

    def validate_description(self, value: str) -> str:
        """Args: value. Returns: normalized description."""
        return value

    def validate_due_at(self, value: datetime | None) -> datetime | None:
        """Args: value. Returns: validated aware datetime or None."""
        if value is None:
            return None
        if timezone.is_naive(value):
            raise serializers.ValidationError("due_at must be timezone-aware")
        return value
