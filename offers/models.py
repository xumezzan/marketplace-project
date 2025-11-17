"""
Offer model for specialist responses to tasks.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Offer(models.Model):
    """
    Offer model representing a specialist's response to a task.
    
    Specialists create offers with a proposed price and message.
    Clients can accept or reject offers.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'
    
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='offers',
        help_text="The task this offer is for"
    )
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
        help_text="The specialist making this offer"
    )
    proposed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price proposed by the specialist"
    )
    message = models.TextField(
        help_text="Message from specialist to client"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current status of the offer"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offers'
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['specialist', 'status']),
        ]
        # Prevent duplicate offers from same specialist for same task
        unique_together = [['task', 'specialist']]
    
    def __str__(self) -> str:
        return f"Offer from {self.specialist.username} for {self.task.title} - {self.proposed_price}"
    
    def can_be_accepted(self) -> bool:
        """Check if offer can be accepted (must be pending and task must be published)."""
        return (
            self.status == self.Status.PENDING and
            self.task.status == self.task.Status.PUBLISHED
        )
    
    def accept(self) -> None:
        """Accept the offer and update related task status."""
        if self.can_be_accepted():
            self.status = self.Status.ACCEPTED
            self.save()
            # Update task status to in_progress
            self.task.status = self.task.Status.IN_PROGRESS
            self.task.save()
            # Reject all other pending offers for this task
            Offer.objects.filter(
                task=self.task,
                status=self.Status.PENDING
            ).exclude(id=self.id).update(status=self.Status.REJECTED)
    
    def reject(self) -> None:
        """Reject the offer."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.REJECTED
            self.save()
