from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import secrets

# Create your models here.
class SensorData(models.Model):
    device = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    temperature_c = models.FloatField()
    amplitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class UserAPIKey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=40, unique=True, default=secrets.token_hex(20))
    active = models.BooleanField(default=True)