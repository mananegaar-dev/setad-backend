from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_now = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    
    