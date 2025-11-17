"""
Админ-панель для модели User.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-интерфейс для кастомной модели User."""
    
    list_display = [
        'username',
        'email',
        'role',
        'city',
        'rating',
        'is_active',
        'is_staff',
        'created_at'
    ]
    list_filter = [
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at'
    ]
    search_fields = [
        'username',
        'email',
        'phone',
        'city',
        'first_name',
        'last_name'
    ]
    ordering = ['-created_at']
    
    # Расширяем стандартные fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'phone', 'city', 'rating')
        }),
    )
    
    # Расширяем add_fieldsets для формы создания пользователя
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'phone', 'city', 'email')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'date_joined', 'last_login']
