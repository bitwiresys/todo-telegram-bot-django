from __future__ import annotations

from typing import Any, TYPE_CHECKING, ClassVar

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from backend.apps.idgen.services import next_id


if TYPE_CHECKING:
    class _UserManagerBase(BaseUserManager["User"]):
        pass
else:
    class _UserManagerBase(BaseUserManager):
        pass


class UserManager(_UserManagerBase):
    def create_user(
        self, telegram_id: int | str, password: str | None = None, **extra_fields: Any
    ) -> User:
        """Args: telegram_id, password, extra_fields. Returns: created user."""
        user = self.model(telegram_id=int(telegram_id), **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(
        self, telegram_id: int | str, password: str | None = None, **extra_fields: Any
    ) -> User:
        """Args: telegram_id, password, extra_fields. Returns: created superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if password is None:
            raise ValueError("Superuser must have password")
        return self.create_user(telegram_id=telegram_id, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=32, primary_key=True, editable=False)
    telegram_id = models.BigIntegerField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD: ClassVar[str] = "telegram_id"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        app_label = "users"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Args: args, kwargs. Returns: None."""
        if not self.id:
            self.id = next_id("user", "usr_", width=24)
        super().save(*args, **kwargs)
