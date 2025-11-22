

class SpecialistDetailView(DetailView):
    """
    Представление для отображения профиля специалиста.
    
    Показывает информацию о специалисте, портфолио, отзывы и форму контакта.
    """
    model = User
    template_name = 'marketplace/specialist_detail.html'
    context_object_name = 'specialist'
    
    def get_queryset(self):
        """Возвращает только специалистов."""
        return User.objects.filter(is_specialist=True).select_related('specialist_profile').prefetch_related(
            'specialist_profile__categories',
            'portfolio_items',
            'reviews_received__client',
            'reviews_received__task'
        )
    
    def get_context_data(self, **kwargs):
        """Добавляет дополнительную информацию в контекст."""
        context = super().get_context_data(**kwargs)
        specialist = self.get_object()
        
        # Получаем профиль
        try:
            profile = specialist.specialist_profile
            context['profile'] = profile
        except:
            context['profile'] = None
        
        # Получаем портфолио
        portfolio_items = specialist.portfolio_items.all().order_by('order', '-created_at')
        context['portfolio_items'] = portfolio_items
        
        # Получаем отзывы
        reviews = specialist.reviews_received.all().select_related('client', 'task').order_by('-created_at')
        context['reviews'] = reviews
        
        # Статистика отзывов
        from django.db.models import Count
        rating_stats = reviews.values('rating').annotate(count=Count('rating')).order_by('-rating')
        context['rating_stats'] = {item['rating']: item['count'] for item in rating_stats}
        
        # Категории
        if context['profile']:
            context['categories'] = context['profile'].categories.all()
        
        return context
