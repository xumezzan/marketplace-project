"""
Админ-панель для моделей marketplace.
"""
from django.contrib import admin
from .models import (
    Category, Subcategory, ClientProfile, SpecialistProfile, 
    Task, Offer, Review, Deal, PortfolioItem, Escrow, AIRequest, TimeSlot,
    Dispute
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
        'moderation_status',
        'auto_structured',
        'budget_display',
        'created_at'
    ]
    list_filter = ['status', 'moderation_status', 'format', 'auto_structured', 'category', 'city', 'created_at']
    search_fields = [
        'title',
        'description',
        'client__username',
        'city',
        'address'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['approve_tasks', 'reject_tasks']
    
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
            'fields': ('status', 'moderation_status', 'auto_structured')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    @admin.action(description='Одобрить выбранные задачи')
    def approve_tasks(self, request, queryset):
        queryset.update(moderation_status=Task.ModerationStatus.APPROVED)
        self.message_user(request, f'Одобрено задач: {queryset.count()}')

    @admin.action(description='Отклонить выбранные задачи')
    def reject_tasks(self, request, queryset):
        queryset.update(moderation_status=Task.ModerationStatus.REJECTED)
        self.message_user(request, f'Отклонено задач: {queryset.count()}')


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
        'moderation_status',
        'created_at'
    ]
    list_filter = ['rating', 'moderation_status', 'created_at']
    search_fields = [
        'specialist__username',
        'client__username',
        'task__title',
        'text'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['approve_reviews', 'reject_reviews']
    
    fieldsets = (
        ('Участники', {
            'fields': ('specialist', 'client', 'task')
        }),
        ('Отзыв', {
            'fields': ('rating', 'text', 'moderation_status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    @admin.action(description='Одобрить выбранные отзывы')
    def approve_reviews(self, request, queryset):
        queryset.update(moderation_status=Review.ModerationStatus.APPROVED)
        self.message_user(request, f'Одобрено отзывов: {queryset.count()}')

    @admin.action(description='Отклонить выбранные отзывы')
    def reject_reviews(self, request, queryset):
        queryset.update(moderation_status=Review.ModerationStatus.REJECTED)
        self.message_user(request, f'Отклонено отзывов: {queryset.count()}')


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


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели AIRequest."""
    list_display = [
        'request_type',
        'user',
        'model_used',
        'success',
        'created_at'
    ]
    list_filter = ['request_type', 'success', 'model_used', 'created_at']
    search_fields = [
        'user__username',
        'user__email',
        'error_message'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Запрос', {
            'fields': ('user', 'request_type', 'model_used')
        }),
        ('Данные', {
            'fields': ('input_data', 'output_data')
        }),
        ('Результат', {
            'fields': ('success', 'error_message')
        }),
        ('Временные метки', {
            'fields': ('created_at',)
        }),
    )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели TimeSlot."""
    list_display = [
        'specialist',
        'date',
        'time_start',
        'time_end',
        'is_available',
        'deal'
    ]
    list_filter = ['date', 'is_available', 'specialist']
    search_fields = [
        'specialist__username',
        'specialist__email'
    ]
    date_hierarchy = 'date'


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели Dispute."""
    list_display = [
        'id',
        'deal',
        'initiator',
        'status',
        'resolution',
        'created_at'
    ]
    list_filter = ['status', 'resolution', 'created_at']
    search_fields = [
        'deal__task__title',
        'initiator__username',
        'reason',
        'description'
    ]
    readonly_fields = ['created_at', 'updated_at', 'resolved_at', 'resolved_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Спор', {
            'fields': ('deal', 'initiator', 'reason', 'description')
        }),
        ('Статус и решение', {
            'fields': ('status', 'resolution', 'resolution_comment')
        }),
        ('Информация о решении', {
            'fields': ('resolved_by', 'resolved_at')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'resolution' in form.changed_data:
            obj.resolved_by = request.user
            from django.utils import timezone
            obj.resolved_at = timezone.now()
            
            # TODO: Implement automatic fund release based on resolution
            # For now, just saving the status
            
        super().save_model(request, obj, form, change)
