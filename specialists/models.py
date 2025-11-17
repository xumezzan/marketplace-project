"""
SpecialistProfile model for specialist-specific information.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class SpecialistProfile(models.Model):
    """
    Specialist profile with categories, experience, rates, and verification status.
    
    Each specialist can have multiple categories and a detailed profile.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='specialist_profile',
        help_text="The user this profile belongs to"
    )
    categories = models.ManyToManyField(
        'categories.Category',
        related_name='specialists',
        blank=True,
        help_text="Service categories this specialist offers"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Bio/description of the specialist"
    )
    years_of_experience = models.PositiveIntegerField(
        default=0,
        help_text="Years of experience in the field"
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Hourly rate in local currency"
    )
    typical_price_range_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Minimum typical price"
    )
    typical_price_range_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum typical price"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the specialist is verified by admin"
    )
    portfolio_links = models.JSONField(
        default=list,
        blank=True,
        help_text="List of portfolio URLs (e.g., ['https://example.com/portfolio'])"
    )
    active = models.BooleanField(
        default=True,
        help_text="Whether the specialist is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'specialist_profiles'
        verbose_name = 'Specialist Profile'
        verbose_name_plural = 'Specialist Profiles'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.user.username} - Specialist Profile"
    
    @property
    def price_range_display(self) -> str:
        """Return formatted price range string."""
        if self.typical_price_range_min and self.typical_price_range_max:
            return f"{self.typical_price_range_min} - {self.typical_price_range_max}"
        elif self.hourly_rate:
            return f"{self.hourly_rate}/hour"
        return "Not specified"
