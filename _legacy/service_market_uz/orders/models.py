from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Order(models.Model):
    """Order created by a client."""
    
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        PUBLISHED = 'published', _('Published')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    category = models.ForeignKey(
        'services.Category',
        on_delete=models.PROTECT,
        related_name='orders'
    )
    description = models.TextField(_('description'))
    price_from = models.DecimalField(
        _('price from'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    price_to = models.DecimalField(
        _('price to'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    is_safe_deal = models.BooleanField(_('is safe deal'), default=False)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )
    deadline = models.DateTimeField(_('deadline'), null=True, blank=True)
    
    # Location
    address = models.CharField(_('address'), max_length=255, blank=True)
    location = models.PointField(_('location'), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return f"Order #{self.id} by {self.client}"


class OrderResponse(models.Model):
    """Response (Bid) from a specialist to an order."""
    
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    price_proposal = models.DecimalField(
        _('price proposal'),
        max_digits=10,
        decimal_places=2
    )
    message = models.TextField(_('message'))
    is_accepted = models.BooleanField(_('is accepted'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('response')
        verbose_name_plural = _('responses')
        unique_together = ('order', 'specialist')

    def __str__(self):
        return f"Response to #{self.order.id} by {self.specialist}"
