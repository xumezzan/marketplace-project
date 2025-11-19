"""
Админ-панель для моделей marketplace.
"""
from django.contrib import admin
from .models import (
    Category, Subcategory, ClientProfile, SpecialistProfile, 
    Task, Offer, Review, Deal, PortfolioItem, Escrow
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Category."""
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Subcategory."""
    list_display = ['name', 'category', 'slug', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели ClientProfile."""
    list_display = ['user', 'address', 'created_at']
    search_fields = ['user__username', 'user__email', 'address']
    filter_horizontal = ['favorite_specialists']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Контактная информация', {
            'fields': ('address', 'preferences')
        }),
        ('Избранные специалисты', {
            'fields': ('favorite_specialists',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


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
        ('Расписание', {
            'fields': ('working_days', 'working_hours_start', 'working_hours_end')
        }),
        ('Зона обслуживания', {
            'fields': ('service_radius_km', 'works_online')
        }),
        ('Верификация', {
            'fields': ('is_verified', 'verification_documents')
        }),
        ('Статус', {
            'fields': ('active',)
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
        'subcategory',
        'format',
        'city',
        'status',
        'auto_structured',
        'budget_display',
        'created_at'
    ]
    list_filter = ['status', 'format', 'auto_structured', 'category', 'city', 'created_at']
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
            'fields': ('client', 'category', 'subcategory', 'title', 'description')
        }),
        ('Формат', {
            'fields': ('format',)
        }),
        ('Бюджет', {
            'fields': ('budget_min', 'budget_max')
        }),
        ('Местоположение', {
            'fields': ('address', 'city', 'latitude', 'longitude')
        }),
        ('Время', {
            'fields': ('preferred_date', 'preferred_time', 'deadline_date')
        }),
        ('Статус и метаданные', {
            'fields': ('status', 'auto_structured')
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


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели PortfolioItem."""
    list_display = [
        'title',
        'specialist',
        'order',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = [
        'title',
        'description',
        'specialist__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('specialist', 'title', 'description', 'image', 'order')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Escrow)
class EscrowAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Escrow."""
    list_display = [
        'deal',
        'amount',
        'status',
        'reserved_at',
        'released_at',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'deal__task__title',
        'deal__client__username',
        'deal__specialist__username'
    ]
    readonly_fields = ['created_at', 'updated_at', 'reserved_at', 'released_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Детали escrow', {
            'fields': ('deal', 'amount', 'status')
        }),
        ('Даты', {
            'fields': ('reserved_at', 'released_at')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
