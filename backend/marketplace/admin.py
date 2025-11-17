"""
Админ-панель для моделей marketplace.
"""
from django.contrib import admin
from .models import Category, SpecialistProfile, Task, Offer, Review, Deal


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Category."""
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SpecialistProfile)
class SpecialistProfileAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели SpecialistProfile."""
    list_display = [
        'user',
        'is_verified',
        'active',
        'years_of_experience',
        'hourly_rate',
        'created_at'
    ]
    list_filter = ['is_verified', 'active', 'created_at']
    search_fields = [
        'user__username',
        'user__email',
        'description'
    ]
    filter_horizontal = ['categories']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Информация о профиле', {
            'fields': ('description', 'years_of_experience', 'categories')
        }),
        ('Ценообразование', {
            'fields': ('hourly_rate', 'typical_price_range_min', 'typical_price_range_max')
        }),
        ('Статус', {
            'fields': ('is_verified', 'active')
        }),
        ('Портфолио', {
            'fields': ('portfolio_links',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Task."""
    list_display = [
        'title',
        'client',
        'category',
        'city',
        'status',
        'budget_display',
        'created_at'
    ]
    list_filter = ['status', 'category', 'city', 'created_at']
    search_fields = [
        'title',
        'description',
        'client__username',
        'city',
        'address'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('client', 'category', 'title', 'description')
        }),
        ('Бюджет', {
            'fields': ('budget_min', 'budget_max')
        }),
        ('Местоположение', {
            'fields': ('address', 'city')
        }),
        ('Время', {
            'fields': ('preferred_date', 'preferred_time')
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Offer."""
    list_display = [
        'task',
        'specialist',
        'proposed_price',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'task__title',
        'specialist__username',
        'message'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Детали предложения', {
            'fields': ('task', 'specialist', 'proposed_price', 'message', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Review."""
    list_display = [
        'specialist',
        'client',
        'task',
        'rating',
        'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = [
        'specialist__username',
        'client__username',
        'task__title',
        'text'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Участники', {
            'fields': ('specialist', 'client', 'task')
        }),
        ('Отзыв', {
            'fields': ('rating', 'text')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Deal."""
    list_display = [
        'task',
        'client',
        'specialist',
        'final_price',
        'status',
        'created_at'
    ]
    list_filter = ['status']
    search_fields = [
        'task__title',
        'specialist__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Детали сделки', {
            'fields': ('task', 'offer', 'client', 'specialist', 'final_price', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
