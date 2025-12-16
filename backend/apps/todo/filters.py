from __future__ import annotations

import django_filters

from backend.apps.todo.models import Task


class TaskFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category_id")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = Task
        fields = ["category", "status"]
