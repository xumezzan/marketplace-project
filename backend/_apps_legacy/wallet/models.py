from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import transaction
import uuid

class Wallet(models.Model):
    specialist = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    currency = models.CharField(max_length=3, default='UZS')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet {self.specialist_id} - {self.balance}"

class Transaction(models.Model):
    class Type(models.TextChoices):
        TOPUP = 'TOPUP', _('Top-up')
        CHARGE_RESPONSE = 'CHARGE_RESPONSE', _('Charge Response')
        CHARGE_COMMISSION = 'CHARGE_COMMISSION', _('Charge Commission')
        REFUND_RESPONSE = 'REFUND_RESPONSE', _('Refund Response')

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=0) # Positive or negative
    description = models.CharField(max_length=255, blank=True)
    
    # Idempotency
    idempotency_key = models.UUIDField(unique=True, default=uuid.uuid4)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Can link to related objects (Request, Deal) via GenericForeignKey if needed, 
    # but for MVP explicit fields or JSONB metadata is simpler.
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.transaction_type} ({self.amount})"
