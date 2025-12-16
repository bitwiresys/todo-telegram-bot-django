from __future__ import annotations

from typing import Any

from django.db import models
from django.utils import timezone
from django.conf import settings

from backend.apps.idgen.services import next_id


class Category(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "todo"
        unique_together = ("owner", "name")

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Args: args, kwargs. Returns: None."""
        if not self.id:
            self.id = next_id("category", "cat_", width=24)
        super().save(*args, **kwargs)


class TaskStatus(models.TextChoices):
    OPEN = "open", "Open"
    DONE = "done", "Done"


class Task(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    status = models.CharField(max_length=16, choices=TaskStatus.choices, default=TaskStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "todo"
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["owner", "due_at"]),
            models.Index(fields=["due_at", "notified_at"]),
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Args: args, kwargs. Returns: None."""
        if self.due_at is not None and timezone.is_naive(self.due_at):
            raise ValueError("due_at must be timezone-aware")
        if not self.id:
            self.id = next_id("task", "tsk_", width=24)
        super().save(*args, **kwargs)
