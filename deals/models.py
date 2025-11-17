"""
Deal/Booking model for completed agreements (optional for MVP).
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Deal(models.Model):
    """
    Deal model representing a confirmed agreement between client and specialist.
    
    This is optional for MVP but useful for tracking completed transactions.
    Can be created when an offer is accepted or manually.
    """
    
    class Status(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', 'Pending Payment'
        PAID = 'paid', 'Paid'
        COMPLETED = 'completed', 'Completed'
        DISPUTED = 'disputed', 'Disputed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    task = models.OneToOneField(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='deal',
        help_text="The task this deal is for"
    )
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deals',
        help_text="The specialist in this deal"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_deals',
        help_text="The client in this deal"
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Final agreed price"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
        help_text="Current status of the deal"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'deals'
        verbose_name = 'Deal'
        verbose_name_plural = 'Deals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['specialist', 'status']),
        ]
    
    def __str__(self) -> str:
        return f"Deal: {self.task.title} - {self.final_price} ({self.get_status_display()})"
    
    def mark_as_paid(self) -> None:
        """Mark the deal as paid."""
        if self.status == self.Status.PENDING_PAYMENT:
            self.status = self.Status.PAID
            self.save()
    
    def mark_as_completed(self) -> None:
        """Mark the deal as completed."""
        if self.status in [self.Status.PAID, self.Status.PENDING_PAYMENT]:
            self.status = self.Status.COMPLETED
            self.save()
            # Also update the task status
            self.task.status = self.task.Status.COMPLETED
            self.task.save()
