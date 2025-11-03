from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserAPIKey

@receiver(user_logged_in)
def activate_api_key(sender, request, user, **kwargs):
    api_key, created = UserAPIKey.objects.get_or_create(user=user)
    api_key.active = True
    api_key.save()

@receiver(user_logged_out)
def deactivate_api_key(sender, request, user, **kwargs):
    try:
        api_key = UserAPIKey.objects.get(user=user)
        api_key.active = False
        api_key.save()
    except UserAPIKey.DoesNotExist:
        pass
