from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Wallet(models.Model):
    """User's digital wallet."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        _('balance'),
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.user} ({self.balance})"


class Transaction(models.Model):
    """Record of financial movement."""
    
    class Type(models.TextChoices):
        DEPOSIT = 'deposit', _('Deposit')
        WITHDRAWAL = 'withdrawal', _('Withdrawal')
        REFUND = 'refund', _('Refund')

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2
    )
    transaction_type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices
    )
    description = models.CharField(_('description'), max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount}"
