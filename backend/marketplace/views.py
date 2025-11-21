"""
Views для marketplace приложения.
"""
import logging
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

logger = logging.getLogger(__name__)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Task, Offer, Deal, Category, Review, PortfolioItem
from .forms import TaskCreateForm, OfferCreateForm, ReviewCreateForm, PortfolioItemForm

User = get_user_model()


# Статические страницы
def safe_deal_view(request):
    """Страница о безопасных сделках (Escrow)"""
    return render(request, 'marketplace/static/safe_deal.html')


def how_it_works_view(request):
    """Страница 'Как это работает'"""
    return render(request, 'marketplace/static/how_it_works.html')


def pricing_view(request):
    """Страница с тарифами"""
    return render(request, 'marketplace/static/pricing.html')


def help_view(request):
    """Страница помощи"""
    return render(request, 'marketplace/static/help.html')


def privacy_policy_view(request):
    """Политика конфиденциальности"""
    return render(request, 'marketplace/static/privacy_policy.html')


def terms_of_service_view(request):
    """Условия использования"""
    return render(request, 'marketplace/static/terms_of_service.html')


def home(request):
    """
    Главная страница (лендинг).
    
    Отображает информацию о платформе, популярные категории и статистику.
    """
    categories = Category.objects.all()[:12]
    tasks_count = Task.objects.filter(status=Task.Status.PUBLISHED).count()
    
    # Получаем реальных специалистов с рейтингом
    specialists = User.objects.filter(
        is_specialist=True, 
        specialist_profile__isnull=False
    ).select_related('specialist_profile').prefetch_related(
        'specialist_profile__categories',
        'portfolio_items'
    ).order_by('-rating')[:4]
    
    specialists_count = User.objects.filter(is_specialist=True).count()
    cities_count = 10  # Заглушка
    
    context = {
        'categories': categories,
        'specialists': specialists,
        'tasks_count': tasks_count,
        'specialists_count': specialists_count,
        'cities_count': cities_count,
    }
    
    return render(request, 'marketplace/home.html', context)


class TaskListView(ListView):
    """
    Представление для отображения списка опубликованных задач.
    
    Показывает только задачи со статусом PUBLISHED (по умолчанию),
    с поддержкой фильтрации по городу, категории, поиску, бюджету и статусу.
    Для специалистов по умолчанию показывает задачи их категорий и города.
    """
    model = Task
    template_name = 'marketplace/tasks_list.html'
    context_object_name = 'tasks'
    paginate_by = 12  # Количество задач на странице
    
    def get_queryset(self):
        """Возвращает отфильтрованные задачи."""
        # Начальный queryset - по умолчанию только опубликованные
        queryset = Task.objects.select_related('client', 'category').order_by('-created_at')
        
        # Получаем все GET-параметры
        city_filter = self.request.GET.get('city', '').strip()
        category_filter = self.request.GET.get('category', '').strip()
        query = self.request.GET.get('q', '').strip()
        price_min = self.request.GET.get('price_min', '').strip()
        price_max = self.request.GET.get('price_max', '').strip()
        status_filter = self.request.GET.get('status', '').strip()
        
        # Проверяем, есть ли явные фильтры в GET-параметрах
        has_explicit_filters = bool(
            city_filter or category_filter or query or price_min or price_max or status_filter
        )
        
        # Фильтр по статусу (если не указан явно, показываем только PUBLISHED)
        if status_filter and status_filter in [s[0] for s in Task.Status.choices]:
            queryset = queryset.filter(status=status_filter)
        elif not has_explicit_filters:
            # Если нет явных фильтров, показываем только опубликованные
            queryset = queryset.filter(status=Task.Status.PUBLISHED)
        
        # Текстовый поиск (q)
        if query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        
        # Фильтр по городу
        if city_filter:
            queryset = queryset.filter(city__icontains=city_filter)
        
        # Фильтр по категории
        if category_filter:
            from .models import Category
            try:
                category = Category.objects.filter(slug=category_filter).first()
                if not category:
                    # Если не найдено по slug, ищем по названию (icontains)
                    category = Category.objects.filter(name__icontains=category_filter).first()
                
                if category:
                    queryset = queryset.filter(category=category)
            except Exception as e:
                logger.error(f"Error filtering by category '{category_filter}': {e}", exc_info=True)
                # Продолжаем без фильтра категории
        
        # Фильтр по бюджету
        if price_min:
            try:
                from django.db.models import Q
                price_min_float = float(price_min)
                queryset = queryset.filter(
                    Q(budget_max__gte=price_min_float) | Q(budget_min__gte=price_min_float)
                )
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid price_min value '{price_min}': {e}")
                # Игнорируем невалидное значение минимальной цены
        
        if price_max:
            try:
                from django.db.models import Q
                price_max_float = float(price_max)
                queryset = queryset.filter(
                    Q(budget_min__lte=price_max_float) | Q(budget_max__lte=price_max_float)
                )
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid price_max value '{price_max}': {e}")
                # Игнорируем невалидное значение максимальной цены
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляет категории и текущие значения фильтров в контекст."""
        context = super().get_context_data(**kwargs)
        
        # Добавляем список категорий для формы фильтров
        from .models import Category
        context['categories'] = Category.objects.all().order_by('name')
        
        # Текущие значения фильтров
        context['current_city'] = self.request.GET.get('city', '').strip()
        context['current_category'] = self.request.GET.get('category', '').strip()
        context['current_query'] = self.request.GET.get('q', '').strip()
        context['current_price_min'] = self.request.GET.get('price_min', '').strip()
        context['current_price_max'] = self.request.GET.get('price_max', '').strip()
        context['current_status'] = self.request.GET.get('status', '').strip()
        
        # Для обратной совместимости
        context['current_filters'] = {
            'city': context['current_city'],
            'category': context['current_category'],
        }
        
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания новой задачи клиентом.
    
    Требует аутентификации и проверяет, что пользователь является клиентом.
    """
    model = Task
    form_class = TaskCreateForm
    template_name = 'marketplace/task_create.html'
    success_url = reverse_lazy('marketplace:my_tasks')
    
    def dispatch(self, request, *args, **kwargs):
        """Проверяет, что пользователь является клиентом."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_client:
            messages.error(request, 'Только клиенты могут создавать задачи.')
            return redirect('marketplace:tasks_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Устанавливает клиента и статус DRAFT при создании."""
        form.instance.client = self.request.user
        form.instance.status = Task.Status.DRAFT
        messages.success(self.request, 'Задача успешно создана! Теперь вы можете опубликовать её.')
        return super().form_valid(form)


class TaskDetailView(DetailView):
    """
    Представление для отображения детальной информации о задаче.
    
    Показывает задачу, все предложения от специалистов и форму для создания предложения.
    """
    model = Task
    template_name = 'marketplace/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        """Возвращает queryset с оптимизацией запросов."""
        return Task.objects.select_related('client', 'category').prefetch_related(
            'offers__specialist',
            'reviews__client'
        )
    
    def get_context_data(self, **kwargs):
        """Добавляет предложения и форму в контекст."""
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        user = self.request.user
        
        # Получаем все предложения для этой задачи
        offers = task.offers.select_related('specialist').order_by('-created_at')
        
        # Для каждого предложения проверяем, есть ли отзыв
        offers_with_ratings = []
        for offer in offers:
            has_review = False
            reviews_count = 0
            if user.is_authenticated and task.status == Task.Status.COMPLETED:
                # Проверяем, есть ли отзыв от этого клиента для этого специалиста
                has_review = Review.objects.filter(
                    task=task,
                    specialist=offer.specialist,
                    client=user
                ).exists()
                reviews_count = Review.objects.filter(specialist=offer.specialist).count()
            
            # Получаем профиль специалиста
            specialist_profile = getattr(offer.specialist, 'specialist_profile', None)
            portfolio_count = offer.specialist.portfolio_items.count()
            
            profession = "Специалист"
            description = ""
            price_range = ""
            
            if specialist_profile:
                first_category = specialist_profile.categories.first()
                if first_category:
                    profession = first_category.name
                description = specialist_profile.description or ""
                price_range = specialist_profile.price_range_display

            offers_with_ratings.append({
                'offer': offer,
                'has_review': has_review,
                'reviews_count': reviews_count,
                'portfolio_count': portfolio_count,
                'profession': profession,
                'description': description,
                'price_range': price_range,
            })
        
        context['offers'] = offers
        context['offers_with_ratings'] = offers_with_ratings
        
        # Проверяем, есть ли уже сделка для этой задачи
        deal = task.deals.first()
        context['deal'] = deal
        
        # Форма для создания предложения (только для специалистов)
        if user.is_authenticated and user.is_specialist:
            from .forms import OfferCreateForm
            from .models import Offer
            
            # Проверяем, может ли пользователь создать предложение
            has_existing_offer = Offer.objects.filter(
                task=task,
                specialist=user
            ).exists()
            
            can_create_offer = (
                task.can_receive_offers() and
                not has_existing_offer and
                task.client != user
            )
            
            context['can_create_offer'] = can_create_offer
            context['has_existing_offer'] = has_existing_offer
            
            if can_create_offer:
                context['offer_form'] = OfferCreateForm()
        
        return context


class AcceptOfferView(LoginRequiredMixin, View):
    """
    Представление для принятия предложения клиентом.
    
    Создает сделку (Deal) и обновляет статусы задачи и предложения.
    """
    def post(self, request, offer_id):
        """Принимает предложение и создает сделку."""
        offer = get_object_or_404(Offer, id=offer_id)
        task = offer.task
        
        # Проверяем права доступа
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация.')
            return redirect('accounts:login')
        
        if task.client != request.user:
            messages.error(request, 'Вы не можете принять это предложение.')
            return redirect('marketplace:task_detail', pk=task.id)
        
        if not offer.can_be_accepted():
            messages.error(request, 'Это предложение нельзя принять.')
            return redirect('marketplace:task_detail', pk=task.id)
        
        # Принимаем предложение (это создаст Deal через сигнал или метод accept)
        offer.accept()
        
        # Создаем сделку
        from .models import Deal
        deal = Deal.objects.create(
            task=task,
            offer=offer,
            client=task.client,
            specialist=offer.specialist,
            final_price=int(offer.proposed_price)
        )
        
        # Создаем Escrow для безопасной сделки
        from .models import Escrow
        from decimal import Decimal
        Escrow.objects.create(
            deal=deal,
            amount=Decimal(str(deal.final_price))
        )
        
        messages.success(request, f'Предложение принято! Сделка создана на сумму {deal.final_price} ₽.')
        return redirect('marketplace:task_detail', pk=task.id)


class MarkDealPaidView(LoginRequiredMixin, View):
    """
    Представление для отметки сделки как оплаченной.
    
    Доступно только клиенту, который создал задачу.
    """
    def post(self, request, deal_id):
        """Отмечает сделку как оплаченную."""
        deal = get_object_or_404(Deal, id=deal_id)
        
        if deal.client != request.user:
            messages.error(request, 'Вы не можете изменить статус этой сделки.')
            return redirect('marketplace:task_detail', pk=deal.task.id)
        
        if deal.status != Deal.Status.PENDING:
            messages.error(request, 'Сделка уже имеет другой статус.')
            return redirect('marketplace:task_detail', pk=deal.task.id)
        
        deal.mark_as_paid()
        
        # Резервируем средства в Escrow
        try:
            if hasattr(deal, 'escrow') and deal.escrow:
                deal.escrow.reserve()
                deal.escrow.lock()  # Блокируем средства (работа начата)
        except Exception as e:
            logger.error(f"Ошибка при работе с Escrow: {e}")
            # Продолжаем выполнение даже если Escrow не работает
        
        messages.success(request, 'Сделка отмечена как оплаченная. Средства зарезервированы.')
        return redirect('marketplace:task_detail', pk=deal.task.id)


class MarkDealCompletedView(LoginRequiredMixin, View):
    """
    Представление для отметки сделки как завершенной.
    
    Доступно только клиенту, который создал задачу.
    """
    def post(self, request, deal_id):
        """Отмечает сделку как завершенную."""
        deal = get_object_or_404(Deal, id=deal_id)
        
        if deal.client != request.user:
            messages.error(request, 'Вы не можете изменить статус этой сделки.')
            return redirect('marketplace:task_detail', pk=deal.task.id)
        
        if deal.status not in [Deal.Status.PAID, Deal.Status.PENDING]:
            messages.error(request, 'Сделка уже завершена или имеет другой статус.')
            return redirect('marketplace:task_detail', pk=deal.task.id)
        
        deal.mark_as_completed()
        
        # Переводим средства исполнителю через Escrow
        try:
            if hasattr(deal, 'escrow') and deal.escrow:
                deal.escrow.release()
        except Exception as e:
            logger.error(f"Ошибка при освобождении Escrow: {e}")
            # Продолжаем выполнение даже если Escrow не работает
        
        messages.success(request, 'Сделка завершена! Средства переведены исполнителю.')
        return redirect('marketplace:task_detail', pk=deal.task.id)


@login_required
def create_review(request, task_id, specialist_id):
    """
    Представление для создания отзыва о специалисте.
    
    Доступно только клиенту после завершения задачи.
    """
    task = get_object_or_404(Task, id=task_id)
    specialist = get_object_or_404(User, id=specialist_id)
    
    # Проверяем права доступа
    if task.client != request.user:
        messages.error(request, 'Вы можете оставить отзыв только по своим задачам.')
        return redirect('marketplace:task_detail', pk=task.id)
    
    if task.status != Task.Status.COMPLETED:
        messages.error(request, 'Отзыв можно оставить только после завершения задачи.')
        return redirect('marketplace:task_detail', pk=task.id)
    
    # Проверяем, есть ли уже отзыв
    existing_review = Review.objects.filter(
        task=task,
        specialist=specialist,
        client=request.user
    ).first()
    
    if request.method == 'POST':
        from .forms import ReviewCreateForm
        form = ReviewCreateForm(request.POST, instance=existing_review)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.specialist = specialist
            review.client = request.user
            review.task = task
            review.save()
            
            messages.success(request, 'Отзыв успешно сохранен!')
            return redirect('marketplace:task_detail', pk=task.id)
    else:
        from .forms import ReviewCreateForm
        form = ReviewCreateForm(instance=existing_review)
    
    context = {
        'task': task,
        'specialist': specialist,
        'form': form,
        'existing_review': existing_review,
    }
    
    return render(request, 'marketplace/review_form.html', context)


@login_required
def my_tasks(request):
    """
    Страница "Мои задачи" для клиентов.
    
    Показывает все задачи, созданные текущим пользователем.
    """
    if not request.user.is_client:
        messages.error(request, 'Эта страница доступна только для клиентов.')
        return redirect('marketplace:tasks_list')
    
    tasks = Task.objects.filter(client=request.user).select_related('category').order_by('-created_at')
    
    context = {
        'tasks': tasks,
    }
    
    return render(request, 'marketplace/my_tasks.html', context)


@login_required
def my_offers(request):
    """
    Страница "Мои отклики" для специалистов.
    
    Показывает все предложения, созданные текущим специалистом.
    """
    if not request.user.is_specialist:
        messages.error(request, 'Эта страница доступна только для специалистов.')
        return redirect('marketplace:tasks_list')
    
    offers = Offer.objects.filter(specialist=request.user).select_related(
        'task', 'task__client', 'task__category'
    ).order_by('-created_at')
    
    context = {
        'offers': offers,
    }
    
    return render(request, 'marketplace/my_offers.html', context)


@login_required
def my_deals(request):
    """
    Страница "Мои сделки" для клиентов и специалистов.
    
    Показывает все сделки, в которых участвует текущий пользователь.
    """
    if request.user.is_client:
        deals = Deal.objects.filter(client=request.user).select_related(
            'task', 'specialist', 'offer'
        ).order_by('-created_at')
        user_role = 'client'
    elif request.user.is_specialist:
        deals = Deal.objects.filter(specialist=request.user).select_related(
            'task', 'client', 'offer'
        ).order_by('-created_at')
        user_role = 'specialist'
    else:
        messages.error(request, 'Эта страница доступна только для клиентов и специалистов.')
        return redirect('marketplace:tasks_list')
    
    context = {
        'deals': deals,
        'user_role': user_role,
    }
    
    return render(request, 'marketplace/my_deals.html', context)


# ============================================
# Новые функции из Profimatch
# ============================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services.ai_service import analyze_task_description
from .models import PortfolioItem, Escrow


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_task_ai(request):
    """
    API endpoint для AI-анализа описания задачи.
    
    Принимает:
    - description: текст описания задачи
    
    Возвращает:
    - title: заголовок
    - category_id: ID категории
    - description: улучшенное описание
    - format: формат (online/offline)
    - budget_min: мин бюджет
    - budget_max: макс бюджет
    - city: город
    - preferred_date: дата
    """
    description = request.data.get('description', '').strip()
    
    if not description:
        return Response(
            {'error': 'Описание задачи обязательно'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from .services.ai_service import AIService
    
    # Используем новый сервис
    result = AIService.parse_task_text(description, user=request.user)
    
    if result.get('error'):
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Если бюджет не определен, пробуем оценить его
    if not result.get('budget_min') and result.get('category_id'):
        estimate = AIService.estimate_price(result)
        if estimate['estimated_min'] > 0:
            result['budget_min'] = estimate['estimated_min']
            result['budget_max'] = estimate['estimated_max']
            result['price_estimated'] = True
    
    return Response(result, status=status.HTTP_200_OK)


class PortfolioListView(LoginRequiredMixin, ListView):
    """
    Список работ в портфолио специалиста.
    """
    model = PortfolioItem
    template_name = 'marketplace/portfolio_list.html'
    context_object_name = 'portfolio_items'
    
    def get_queryset(self):
        return PortfolioItem.objects.filter(specialist=self.request.user).order_by('order', '-created_at')
        
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_specialist:
            messages.error(request, 'Портфолио доступно только специалистам.')
            return redirect('marketplace:tasks_list')
        return super().dispatch(request, *args, **kwargs)


class PortfolioCreateView(LoginRequiredMixin, CreateView):
    """
    Добавление работы в портфолио.
    """
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = 'marketplace/portfolio_form.html'
    success_url = reverse_lazy('marketplace:portfolio_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_specialist:
            messages.error(request, 'Только специалисты могут добавлять работы.')
            return redirect('marketplace:tasks_list')
        return super().dispatch(request, *args, **kwargs)
        
    def form_valid(self, form):
        form.instance.specialist = self.request.user
        messages.success(self.request, 'Работа добавлена в портфолио!')
        return super().form_valid(form)


class PortfolioUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование работы в портфолио.
    """
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = 'marketplace/portfolio_form.html'
    success_url = reverse_lazy('marketplace:portfolio_list')
    
    def get_queryset(self):
        return PortfolioItem.objects.filter(specialist=self.request.user)
        
    def form_valid(self, form):
        messages.success(self.request, 'Работа обновлена!')
        return super().form_valid(form)


class PortfolioDeleteView(LoginRequiredMixin, DeleteView):
    """
    Удаление работы из портфолио.
    """
    model = PortfolioItem
    template_name = 'marketplace/portfolio_confirm_delete.html'
    success_url = reverse_lazy('marketplace:portfolio_list')
    
    def get_queryset(self):
        return PortfolioItem.objects.filter(specialist=self.request.user)
        
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Работа удалена из портфолио.')
        return super().delete(request, *args, **kwargs)


def get_specialist_data(request, specialist_id):
    """
    API endpoint для получения данных специалиста в JSON формате.
    Используется для модального окна профиля специалиста.
    """
    try:
        specialist = get_object_or_404(User, id=specialist_id, is_specialist=True)
        
        # Получаем профиль специалиста
        try:
            profile = specialist.specialist_profile
        except:
            return JsonResponse({'error': 'Профиль специалиста не найден'}, status=404)
        
        # Получаем портфолио
        portfolio_items = PortfolioItem.objects.filter(specialist=specialist).order_by('order')
        portfolio_data = [{
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'image_url': item.image.url if item.image else None,
        } for item in portfolio_items]
        
        # Получаем отзывы
        reviews = Review.objects.filter(specialist=specialist).select_related('task', 'client').order_by('-created_at')[:10]
        reviews_data = [{
            'id': review.id,
            'client_name': review.client.username,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%d.%m.%Y'),
            'task_title': review.task.title if review.task else None,
        } for review in reviews]
        
        # Формируем ответ
        data = {
            'id': specialist.id,
            'username': specialist.username,
            'avatar_url': specialist.avatar.url if specialist.avatar else f'https://ui-avatars.com/api/?name={specialist.username}&background=random',
            'rating': float(specialist.rating) if specialist.rating else 0,
            'reviews_count': reviews.count(),
            'profession': profile.categories.first().name if profile.categories.exists() else 'Специалист',
            'description': profile.description or 'Описание отсутствует',
            'years_of_experience': profile.years_of_experience,
            'hourly_rate': str(profile.hourly_rate) if profile.hourly_rate else None,
            'price_range': f'{profile.typical_price_range_min}-{profile.typical_price_range_max} ₽' if profile.typical_price_range_min else 'По договоренности',
            'is_verified': profile.is_verified,
            'portfolio': portfolio_data,
            'reviews': reviews_data,
        }
        
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error fetching specialist data: {e}")
        return JsonResponse({'error': 'Ошибка при получении данных'}, status=500)
