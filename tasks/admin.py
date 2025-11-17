"""
Admin configuration for Task model.
"""
from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model."""
    list_display = ['title', 'client', 'category', 'city', 'status', 'budget_display', 'created_at']
    list_filter = ['status', 'category', 'city', 'created_at']
    search_fields = ['title', 'description', 'client__username', 'city', 'address']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('client', 'category', 'title', 'description')
        }),
        ('Budget', {
            'fields': ('budget_min', 'budget_max')
        }),
        ('Location', {
            'fields': ('address', 'city')
        }),
        ('Timing', {
            'fields': ('preferred_date', 'preferred_time')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
