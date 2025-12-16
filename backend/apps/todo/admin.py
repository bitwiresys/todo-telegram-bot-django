from typing import TYPE_CHECKING

from django.contrib import admin

from backend.apps.todo.models import Category, Task


if TYPE_CHECKING:
    class _CategoryAdminBase(admin.ModelAdmin[Category]):
        pass

    class _TaskAdminBase(admin.ModelAdmin[Task]):
        pass
else:
    class _CategoryAdminBase(admin.ModelAdmin):
        pass

    class _TaskAdminBase(admin.ModelAdmin):
        pass


@admin.register(Category)
class CategoryAdmin(_CategoryAdminBase):
    list_display = ("id", "owner", "name", "created_at")
    search_fields = ("id", "name", "owner__telegram_id")


@admin.register(Task)
class TaskAdmin(_TaskAdminBase):
    list_display = ("id", "owner", "title", "status", "due_at", "created_at", "notified_at")
    list_filter = ("status",)
    search_fields = ("id", "title", "owner__telegram_id")
