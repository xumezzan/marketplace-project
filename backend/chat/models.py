from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """
    Модель диалога между двумя пользователями.
    Обычно привязана к сделке или задаче.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        verbose_name='участники'
    )
    deal = models.OneToOneField(
        'marketplace.Deal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversation',
        verbose_name='сделка'
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'диалог'
        verbose_name_plural = 'диалоги'
        
    def __str__(self):
        return f"Диалог {self.id}"


class Message(models.Model):
    """
    Модель сообщения в диалоге.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='диалог'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='отправитель'
    )
    text = models.TextField('текст')
    is_read = models.BooleanField('прочитано', default=False)
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        
    def __str__(self):
        return f"Сообщение от {self.sender.username}"
