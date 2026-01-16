from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User
from marketplace.models import SpecialistProfile, ClientProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Автоматическое создание профилей при регистрации пользователя.
    """
    if created:
        if instance.is_specialist:
            SpecialistProfile.objects.get_or_create(user=instance)
        
        if instance.is_client:
            ClientProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сохранение профилей при сохранении пользователя.
    """
    # Если роль была добавлена позже (не при создании), создаем профиль
    if instance.is_specialist and not hasattr(instance, 'specialist_profile'):
        SpecialistProfile.objects.create(user=instance)
        
    if instance.is_client and not hasattr(instance, 'client_profile'):
        ClientProfile.objects.create(user=instance)
