from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    """
    User notification.
    """
    class Type(models.TextChoices):
        SYSTEM = 'system', _('System')
        ORDER = 'order', _('Order')
        MESSAGE = 'message', _('Message')
        PAYMENT = 'payment', _('Payment')
        
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('user')
    )
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    notification_type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.SYSTEM
    )
    is_read = models.BooleanField(_('is read'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.user})"
