from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    """
    Модель уведомления пользователя.
    """
    class Type(models.TextChoices):
        INFO = 'info', 'Инфо'
        SUCCESS = 'success', 'Успех'
        WARNING = 'warning', 'Внимание'
        ERROR = 'error', 'Ошибка'
        
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='получатель'
    )
    title = models.CharField('заголовок', max_length=255)
    message = models.TextField('сообщение')
    notification_type = models.CharField(
        'тип',
        max_length=20,
        choices=Type.choices,
        default=Type.INFO
    )
    is_read = models.BooleanField('прочитано', default=False)
    link = models.CharField('ссылка', max_length=500, blank=True, null=True)
    
    # Generic relation для связи с любым объектом (Task, Offer, Deal)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'уведомление'
        verbose_name_plural = 'уведомления'
        
    def __str__(self):
        return f"{self.title} -> {self.recipient.username}"
