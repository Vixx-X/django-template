from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, EmailDevice

@receiver(post_save, sender=User)
def creating_user_settings(sender, instance, created, raw, **kwargs):
    """Creating the user device for a new User"""

    if created and not raw:
        EmailDevice.objects.create(user=instance, name=f"personal device for user {instance.pk}", confirmed=True)

