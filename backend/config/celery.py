import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send-due-notifications-every-minute": {
        "task": "backend.apps.notifications.tasks.send_due_notifications",
        "schedule": 60.0,
    }
}
