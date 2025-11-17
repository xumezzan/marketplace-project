"""
Admin configuration for User model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    list_display = ['username', 'email', 'role', 'city', 'rating', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'phone', 'city']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Marketplace Info', {
            'fields': ('role', 'phone', 'city', 'rating')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Marketplace Info', {
            'fields': ('role', 'phone', 'city')
        }),
    )
