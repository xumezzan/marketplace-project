from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Wallet

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Автоматическое создание кошелька при регистрации пользователя.
    """
    if created:
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_wallet(sender, instance, **kwargs):
    """
    Сохранение кошелька при обновлении пользователя.
    """
    if hasattr(instance, 'wallet'):
        instance.wallet.save()
