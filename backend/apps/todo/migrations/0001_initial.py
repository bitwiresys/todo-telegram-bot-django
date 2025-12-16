from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.CharField(editable=False, max_length=32, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="categories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("owner", "name")},
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.CharField(editable=False, max_length=32, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=256)),
                ("description", models.TextField(blank=True)),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("done", "Done")],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("notified_at", models.DateTimeField(blank=True, null=True)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tasks",
                        to="todo.category",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(fields=["owner", "status"], name="todo_task_owner_i_49c3cc_idx"),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(fields=["owner", "due_at"], name="todo_task_owner_i_8e73fd_idx"),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(fields=["due_at", "notified_at"], name="todo_task_due_at_4d11aa_idx"),
        ),
    ]
