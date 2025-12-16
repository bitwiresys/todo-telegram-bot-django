from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Sequence",
            fields=[
                ("name", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("value", models.BigIntegerField()),
            ],
        ),
    ]
