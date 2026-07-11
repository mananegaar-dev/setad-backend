from django.db import models
from django.contrib.auth import get_user_model
import django_jalali.db.models as jmodels
from excel_app.models import Fields


User = get_user_model()


class UserActivityLog(models.Model):

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activities"
    )

    actor_id_cache = models.IntegerField(null=True, blank=True)

    action = models.CharField(max_length=20)

    document = models.ForeignKey(
        Fields,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )

    document_id_cache = models.IntegerField(null=True, blank=True)

    message = models.TextField()

    created_at = jmodels.jDateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
