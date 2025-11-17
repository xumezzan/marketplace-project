"""
Admin configuration for Offer model.
"""
from django.contrib import admin
from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin interface for Offer model."""
    list_display = ['task', 'specialist', 'proposed_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['task__title', 'specialist__username', 'message']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Offer Details', {
            'fields': ('task', 'specialist', 'proposed_price', 'message', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
