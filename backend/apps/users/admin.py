from typing import TYPE_CHECKING

from django.contrib import admin

from backend.apps.users.models import User


if TYPE_CHECKING:
    class _UserAdminBase(admin.ModelAdmin[User]):
        pass
else:
    class _UserAdminBase(admin.ModelAdmin):
        pass


@admin.register(User)
class UserAdmin(_UserAdminBase):
    list_display = ("id", "telegram_id", "is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("id", "telegram_id")
    list_filter = ("is_staff", "is_superuser", "is_active")
