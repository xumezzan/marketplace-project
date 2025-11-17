"""
Task model for client service requests.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Task(models.Model):
    """
    Task model representing a client's service request.
    
    Clients create tasks with details like category, description, budget,
    location, and preferred time. Specialists can then respond with offers.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="The client who created this task"
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text="Service category for this task"
    )
    title = models.CharField(
        max_length=200,
        help_text="Task title/summary"
    )
    description = models.TextField(
        help_text="Detailed description of the task"
    )
    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Minimum budget"
    )
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum budget"
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Full address or location text"
    )
    city = models.CharField(
        max_length=100,
        help_text="City where the task should be performed"
    )
    preferred_date = models.DateField(
        blank=True,
        null=True,
        help_text="Preferred date for the service"
    )
    preferred_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Preferred time for the service"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text="Current status of the task"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'city']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self) -> str:
        return f"{self.title} - {self.client.username}"
    
    @property
    def budget_display(self) -> str:
        """Return formatted budget string."""
        if self.budget_min and self.budget_max:
            return f"{self.budget_min} - {self.budget_max}"
        elif self.budget_min:
            return f"From {self.budget_min}"
        elif self.budget_max:
            return f"Up to {self.budget_max}"
        return "Budget not specified"
    
    def can_be_edited(self) -> bool:
        """Check if task can still be edited (only draft or published)."""
        return self.status in [self.Status.DRAFT, self.Status.PUBLISHED]
    
    def can_receive_offers(self) -> bool:
        """Check if task can receive new offers."""
        return self.status == self.Status.PUBLISHED
