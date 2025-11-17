"""
User model for the marketplace application.

Extends Django's AbstractUser to add role-based authentication
and marketplace-specific fields.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Custom user model with role-based access (client or specialist).
    
    Extends Django's AbstractUser to add:
    - Role selection (client/specialist)
    - Phone number
    - City
    - Average rating
    """
    
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        SPECIALIST = 'specialist', 'Specialist'
    
    # Additional fields
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        help_text="User role: client or specialist"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="User phone number"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User city"
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)],
        help_text="Average rating (0.00 to 5.00)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_specialist(self) -> bool:
        """Check if user is a specialist."""
        return self.role == self.Role.SPECIALIST
    
    @property
    def is_client(self) -> bool:
        """Check if user is a client."""
        return self.role == self.Role.CLIENT
