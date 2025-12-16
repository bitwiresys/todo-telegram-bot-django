from django.db import models


class Sequence(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    value = models.BigIntegerField()

    class Meta:
        app_label = "idgen"
