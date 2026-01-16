from django.db import models
from django.conf import settings
from apps.requests.models import Request
from django.utils.translation import gettext_lazy as _

class Response(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')

    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='responses')
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='responses')
    
    tariff_type = models.CharField(max_length=20) # Snapshot of what tariff was applied
    price_paid = models.DecimalField(max_digits=12, decimal_places=0) # Snapshot of cost
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True)
    
    viewed_at_by_client = models.DateTimeField(null=True, blank=True)
    refund_processed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request', 'specialist')

    def __str__(self):
        return f"Response {self.id} on {self.request_id} by {self.specialist_id}"
