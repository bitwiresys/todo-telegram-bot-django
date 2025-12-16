from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from backend.apps.todo.api import CategoryViewSet, TaskViewSet
from backend.apps.users.api import EnsureUserView

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/ensure/", EnsureUserView.as_view(), name="ensure-user"),
    path("api/", include(router.urls)),
]
