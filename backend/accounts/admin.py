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
        'is_client',
        'is_specialist',
        'city',
        'rating',
        'is_active',
        'is_staff',
        'created_at'
    ]
    list_filter = [
        'is_client',
        'is_specialist',
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
        ('Роли', {
            'fields': ('is_client', 'is_specialist')
        }),
        ('Дополнительная информация', {
            'fields': ('phone', 'city', 'rating', 'avatar')
        }),
    )
    
    # Расширяем add_fieldsets для формы создания пользователя
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Роли', {
            'fields': ('is_client', 'is_specialist')
        }),
        ('Дополнительная информация', {
            'fields': ('phone', 'city', 'email')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'date_joined', 'last_login']
