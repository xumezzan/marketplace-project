"""
Admin configuration for SpecialistProfile model.
"""
from django.contrib import admin
from .models import SpecialistProfile


@admin.register(SpecialistProfile)
class SpecialistProfileAdmin(admin.ModelAdmin):
    """Admin interface for SpecialistProfile model."""
    list_display = ['user', 'is_verified', 'active', 'years_of_experience', 'hourly_rate', 'created_at']
    list_filter = ['is_verified', 'active', 'created_at']
    search_fields = ['user__username', 'user__email', 'description']
    filter_horizontal = ['categories']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Info', {
            'fields': ('description', 'years_of_experience', 'categories')
        }),
        ('Pricing', {
            'fields': ('hourly_rate', 'typical_price_range_min', 'typical_price_range_max')
        }),
        ('Status', {
            'fields': ('is_verified', 'active')
        }),
        ('Portfolio', {
            'fields': ('portfolio_links',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
