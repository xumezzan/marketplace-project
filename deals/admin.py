"""
Admin configuration for Deal model.
"""
from django.contrib import admin
from .models import Deal


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """Admin interface for Deal model."""
    list_display = ['task', 'client', 'specialist', 'final_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['task__title', 'client__username', 'specialist__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Deal Details', {
            'fields': ('task', 'client', 'specialist', 'final_price', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
