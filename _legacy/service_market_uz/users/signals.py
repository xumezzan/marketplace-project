from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ClientProfile

@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    """
    Automatically create a ClientProfile for every new user.
    SpecialistProfile is created manually or via a separate flow.
    """
    if created:
        ClientProfile.objects.create(user=instance)
