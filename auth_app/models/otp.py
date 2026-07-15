from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid


User = get_user_model()

OTP_EXP = 120

class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    otp_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_now = models.DateTimeField(auto_now_add=True)
    expire = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expire

    def save(self, *args, **kwargs):
        if not self.expire:
            self.expire = timezone.now() + timedelta(seconds=OTP_EXP)
        super().save(*args, **kwargs)

    
    