from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=12, unique=True, null=True, blank=True)

    areas = models.ManyToManyField(
        "excel_app.Area",
        blank=True,
        related_name="users",
        verbose_name="مناطق قابل دسترسی"
    )