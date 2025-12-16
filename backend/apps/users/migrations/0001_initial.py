from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("idgen", "0001_initial"),
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.CharField(editable=False, max_length=32, primary_key=True, serialize=False)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                ("is_superuser", models.BooleanField(default=False)),
                ("telegram_id", models.BigIntegerField(unique=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                (
                    "groups",
                    models.ManyToManyField(blank=True, related_name="user_set", to="auth.group"),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(blank=True, related_name="user_set", to="auth.permission"),
                ),
            ],
        ),
    ]
