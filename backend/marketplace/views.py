"""
Views для marketplace приложения.
"""
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Task, Offer, Deal, Category, Review
from .forms import TaskCreateForm, OfferCreateForm, ReviewCreateForm

User = get_user_model()


def home(request):
    """
    Главная страница (лендинг).
    
    Отображает информацию о платформе, популярные категории и статистику.
    """
    categories = Category.objects.all()[:12]
    tasks_count = Task.objects.filter(status=Task.Status.PUBLISHED).count()
    specialists_count = 1200  # Заглушка
    cities_count = 10  # Заглушка
    
    context = {
        'categories': categories,
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
                # Сначала пробуем найти по slug
                category = Category.objects.filter(slug=category_filter).first()
                if not category:
                    # Если не найдено по slug, ищем по названию (icontains)
                    category = Category.objects.filter(name__icontains=category_filter).first()
                
                if category:
                    queryset = queryset.filter(category=category)
            except Exception:
                pass
        
        # Фильтр по бюджету (price_min / price_max)
        from django.db.models import Q
        budget_filters = Q()
        
        if price_min:
            try:
                price_min_value = float(price_min)
                # Задачи, где максимальный бюджет >= указанного минимума
                # или минимальный бюджет >= указанного минимума
                budget_filters &= (
                    Q(budget_max__gte=price_min_value) | 
                    Q(budget_min__gte=price_min_value) |
                    (Q(budget_min__isnull=True) & Q(budget_max__gte=price_min_value))
                )
            except (ValueError, TypeError):
                pass
        
        if price_max:
            try:
                price_max_value = float(price_max)
                # Задачи, где минимальный бюджет <= указанного максимума
                # или максимальный бюджет <= указанного максимума
                budget_filters &= (
                    Q(budget_min__lte=price_max_value) | 
                    Q(budget_max__lte=price_max_value) |
                    (Q(budget_max__isnull=True) & Q(budget_min__lte=price_max_value))
                )
            except (ValueError, TypeError):
                pass
        
        if budget_filters:
            queryset = queryset.filter(budget_filters)
        
        # Если нет явных фильтров и пользователь - специалист, применяем фильтры по умолчанию
        if not has_explicit_filters and self.request.user.is_authenticated and self.request.user.is_specialist:
            try:
                specialist_profile = self.request.user.specialist_profile
                
                # Фильтр по городу специалиста
                if specialist_profile.user.city:
                    queryset = queryset.filter(city__icontains=specialist_profile.user.city)
                
                # Фильтр по категориям специалиста
                if specialist_profile.categories.exists():
                    category_ids = specialist_profile.categories.values_list('id', flat=True)
                    queryset = queryset.filter(category_id__in=category_ids)
            except Exception:
                pass
        
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
    Представление для создания новой задачи.
    
    Доступно только авторизованным пользователям с ролью CLIENT.
    Автоматически устанавливает клиента и статус DRAFT.
    """
    model = Task
    form_class = TaskCreateForm
    template_name = 'marketplace/task_create.html'
    success_url = reverse_lazy('marketplace:tasks_list')
    
    def dispatch(self, request, *args, **kwargs):
        """Проверка, что пользователь является клиентом."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_client:
            messages.error(
                request,
                'Только клиенты могут создавать задачи. '
                'Если вы специалист, создайте профиль специалиста.'
            )
            return redirect('marketplace:tasks_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Устанавливает клиента и статус при сохранении формы."""
        form.instance.client = self.request.user
        form.instance.status = Task.Status.DRAFT
        messages.success(
            self.request,
            'Задача успешно создана! Вы можете опубликовать её позже.'
        )
        return super().form_valid(form)


class TaskDetailView(DetailView):
    """
    Представление для отображения деталей задачи.
    
    Показывает:
    - Детали задачи
    - Форму для создания оффера (для специалистов)
    - Список всех офферов по задаче
    """
    model = Task
    template_name = 'marketplace/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        """Оптимизация запросов к БД."""
        return Task.objects.select_related('client', 'category').prefetch_related('offers__specialist')
    
    def get_context_data(self, **kwargs):
        """Добавляет форму оффера и список офферов в контекст."""
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        
        # Получаем все офферы для этой задачи с информацией о рейтингах
        from .models import Review
        offers = Offer.objects.filter(task=task).select_related('specialist').order_by('-created_at')
        
        # Добавляем информацию о рейтинге и количестве отзывов для каждого специалиста
        offers_with_ratings = []
        for offer in offers:
            reviews_count = Review.objects.filter(specialist=offer.specialist).count()
            # Проверяем, оставлен ли уже отзыв от текущего пользователя для этого специалиста
            has_review = False
            if self.request.user.is_authenticated and self.request.user.is_client:
                has_review = Review.objects.filter(
                    task=task,
                    specialist=offer.specialist,
                    client=self.request.user
                ).exists()
            
            offers_with_ratings.append({
                'offer': offer,
                'reviews_count': reviews_count,
                'has_review': has_review,
            })
        
        context['offers_with_ratings'] = offers_with_ratings
        context['offers'] = offers  # Для обратной совместимости
        
        # Проверяем, есть ли сделка для этой задачи
        deal = Deal.objects.filter(task=task).first()
        context['deal'] = deal
        
        # Проверяем, может ли текущий пользователь создать оффер
        can_create_offer = False
        has_existing_offer = False
        
        # Если сделка есть, нельзя создавать новые офферы
        if not deal and self.request.user.is_authenticated:
            if self.request.user.is_specialist:
                # Проверяем, может ли задача принимать офферы
                can_create_offer = task.can_receive_offers()
                # Проверяем, есть ли уже оффер от этого специалиста
                has_existing_offer = Offer.objects.filter(
                    task=task,
                    specialist=self.request.user
                ).exists()
        
        context['can_create_offer'] = can_create_offer and not has_existing_offer
        context['has_existing_offer'] = has_existing_offer
        
        # Форма для создания оффера
        if self.request.method == 'POST' and 'offer_form' in self.request.POST:
            context['offer_form'] = OfferCreateForm(self.request.POST)
        else:
            context['offer_form'] = OfferCreateForm()
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка POST-запроса для создания оффера."""
        self.object = self.get_object()
        task = self.object
        
        # Проверка авторизации
        if not request.user.is_authenticated:
            messages.error(request, 'Необходимо войти в систему для создания предложения.')
            return redirect('marketplace:task_detail', pk=task.pk)
        
        # Проверка роли
        if not request.user.is_specialist:
            messages.error(request, 'Только специалисты могут создавать предложения.')
            return redirect('marketplace:task_detail', pk=task.pk)
        
        # Проверка, может ли задача принимать офферы
        if not task.can_receive_offers():
            messages.error(request, 'Эта задача больше не принимает предложения.')
            return redirect('marketplace:task_detail', pk=task.pk)
        
        # Проверка, нет ли уже оффера от этого специалиста
        if Offer.objects.filter(task=task, specialist=request.user).exists():
            messages.error(request, 'Вы уже отправили предложение по этой задаче.')
            return redirect('marketplace:task_detail', pk=task.pk)
        
        # Обработка формы оффера
        form = OfferCreateForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.task = task
            offer.specialist = request.user
            offer.status = Offer.Status.PENDING
            offer.save()
            
            messages.success(
                request,
                'Ваше предложение успешно отправлено! Клиент получит уведомление.'
            )
            return redirect('marketplace:task_detail', pk=task.pk)
        else:
            # Если форма невалидна, возвращаем страницу с ошибками
            context = self.get_context_data()
            context['offer_form'] = form
            return self.render_to_response(context)
    
    def get(self, request, *args, **kwargs):
        """Обработка GET-запроса."""
        return super().get(request, *args, **kwargs)
    


class AcceptOfferView(LoginRequiredMixin, View):
    """
    View для принятия оффера клиентом.
    
    Создает Deal и изменяет статусы Task и Offer.
    """
    
    def post(self, request, offer_id):
        """Обработка принятия оффера."""
        offer = get_object_or_404(Offer, id=offer_id)
        task = offer.task
        
        # Проверка, что пользователь является клиентом
        if not request.user.is_client:
            messages.error(request, 'Только клиенты могут принимать предложения.')
            return redirect('marketplace:task_detail', pk=task.pk)
        
        # Проверка, что пользователь является владельцем задачи
        if request.user != task.client:
            messages.error(request, 'Вы можете принимать предложения только по своим задачам.')
            return redirect('marketplace:task_detail', pk=task.pk)
        
        # Проверка, можно ли принять оффер
        if not offer.can_be_accepted():
            messages.error(request, 'Это предложение нельзя принять.')
            return redirect('marketplace:task_detail', pk=task.pk)
        
        # Проверка, нет ли уже сделки для этой задачи
        if Deal.objects.filter(task=task).exists():
            messages.error(request, 'По этой задаче уже создана сделка.')
            return redirect('marketplace:task_detail', pk=task.pk)
        
        # Создаем сделку
        deal = Deal.objects.create(
            task=task,
            offer=offer,
            client=task.client,
            specialist=offer.specialist,
            final_price=int(offer.proposed_price),  # Конвертируем Decimal в int
            status=Deal.Status.PENDING
        )
        
        # Принимаем оффер (это также обновит статус задачи и отклонит другие офферы)
        offer.accept()
        
        messages.success(
            request,
            f'Предложение принято! Создана сделка на сумму {offer.proposed_price}.'
        )
        
        return redirect('marketplace:task_detail', pk=task.pk)


class MarkDealPaidView(LoginRequiredMixin, View):
    """View для отметки сделки как оплаченной."""
    
    def post(self, request, deal_id):
        """Обработка отметки оплаты."""
        deal = get_object_or_404(Deal, id=deal_id)
        
        # Проверка прав (только клиент может отметить оплату)
        if not request.user.is_client:
            messages.error(request, 'Только клиенты могут отмечать оплату.')
            return redirect('marketplace:task_detail', pk=deal.task.pk)
        
        if request.user != deal.client:
            messages.error(request, 'Вы можете отмечать оплату только по своим сделкам.')
            return redirect('marketplace:task_detail', pk=deal.task.pk)
        
        deal.mark_as_paid()
        messages.success(request, 'Сделка отмечена как оплаченная.')
        
        return redirect('marketplace:task_detail', pk=deal.task.pk)


class MarkDealCompletedView(LoginRequiredMixin, View):
    """View для отметки сделки как завершенной."""
    
    def post(self, request, deal_id):
        """Обработка отметки завершения."""
        deal = get_object_or_404(Deal, id=deal_id)
        
        # Проверка прав (только клиент может отметить завершение)
        if not request.user.is_client:
            messages.error(request, 'Только клиенты могут отмечать завершение.')
            return redirect('marketplace:task_detail', pk=deal.task.pk)
        
        if request.user != deal.client:
            messages.error(request, 'Вы можете отмечать завершение только по своим сделкам.')
            return redirect('marketplace:task_detail', pk=deal.task.pk)
        
        deal.mark_as_completed()
        messages.success(request, 'Сделка отмечена как завершенная.')
        
        return redirect('marketplace:task_detail', pk=deal.task.pk)


@login_required
def create_review(request, task_id, specialist_id):
    """
    View для создания отзыва клиентом о специалисте.
    
    Только залогиненный пользователь с ролью CLIENT может оставить отзыв.
    Проверяет, что пользователь является клиентом задачи и что специалист откликался на задачу.
    """
    # Проверка роли
    if not request.user.is_client:
        messages.error(request, 'Только клиенты могут оставлять отзывы.')
        return redirect('marketplace:tasks_list')
    
    # Получаем задачу и специалиста
    task = get_object_or_404(Task, id=task_id)
    specialist = get_object_or_404(User, id=specialist_id, role=User.Role.SPECIALIST)
    
    # Проверка, что пользователь является клиентом задачи
    if request.user != task.client:
        messages.error(request, 'Вы можете оставлять отзывы только по своим задачам.')
        return redirect('marketplace:task_detail', pk=task.id)
    
    # Проверка, что специалист откликался на эту задачу
    if not Offer.objects.filter(task=task, specialist=specialist).exists():
        messages.error(request, 'Этот специалист не откликался на данную задачу.')
        return redirect('marketplace:task_detail', pk=task.id)
    
    # Проверка, не оставлен ли уже отзыв
    existing_review = Review.objects.filter(
        task=task,
        specialist=specialist,
        client=request.user
    ).first()
    
    if existing_review:
        messages.warning(request, 'Вы уже оставили отзыв по этой задаче для данного специалиста.')
        return redirect('marketplace:task_detail', pk=task.id)
    
    if request.method == 'POST':
        form = ReviewCreateForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.task = task
            review.specialist = specialist
            review.client = request.user
            review.save()
            # Рейтинг пересчитается автоматически через метод save модели Review
            messages.success(request, 'Отзыв успешно добавлен!')
            return redirect('marketplace:task_detail', pk=task.id)
    else:
        form = ReviewCreateForm()
    
    context = {
        'form': form,
        'task': task,
        'specialist': specialist,
    }
    
    return render(request, 'marketplace/review_form.html', context)


@login_required
def my_tasks(request):
    """
    View для отображения списка задач текущего клиента.
    
    Доступно только для пользователей с ролью CLIENT.
    Поддерживает фильтрацию по статусу через GET-параметр.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Необходимо войти в систему.')
        return redirect('marketplace:tasks_list')
    
    if not request.user.is_client:
        messages.error(request, 'Эта страница доступна только для клиентов.')
        return redirect('marketplace:tasks_list')
    
    # Получаем все задачи клиента
    tasks = Task.objects.filter(client=request.user).select_related('category').order_by('-created_at')
    
    # Фильтр по статусу
    status_filter = request.GET.get('status', '').strip()
    current_status = ''
    
    if status_filter:
        # Проверяем, что статус валидный
        valid_statuses = [Task.Status.PUBLISHED, Task.Status.IN_PROGRESS, Task.Status.COMPLETED, Task.Status.DRAFT, Task.Status.CANCELLED]
        if status_filter in [s[0] for s in Task.Status.choices]:
            tasks = tasks.filter(status=status_filter)
            current_status = status_filter
    
    # Добавляем количество откликов для каждой задачи
    from django.db.models import Count
    tasks = tasks.annotate(offers_count=Count('offers'))
    
    context = {
        'tasks': tasks,
        'current_status': current_status,
    }
    
    return render(request, 'marketplace/my_tasks.html', context)


@login_required
def my_offers(request):
    """
    View для отображения списка откликов текущего специалиста.
    
    Доступно только для пользователей с ролью SPECIALIST.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Необходимо войти в систему.')
        return redirect('marketplace:tasks_list')
    
    if not request.user.is_specialist:
        messages.error(request, 'Эта страница доступна только для специалистов.')
        return redirect('marketplace:tasks_list')
    
    # Получаем все отклики специалиста с связанными задачами
    offers = Offer.objects.filter(
        specialist=request.user
    ).select_related('task', 'task__category', 'task__client').order_by('-created_at')
    
    context = {
        'offers': offers,
    }
    
    return render(request, 'marketplace/my_offers.html', context)


@login_required
def my_deals(request):
    """
    View для отображения списка сделок текущего пользователя.
    
    Для клиентов показывает сделки, где они являются клиентом.
    Для специалистов показывает сделки, где они являются специалистом.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Необходимо войти в систему.')
        return redirect('marketplace:tasks_list')
    
    # Определяем, какие сделки показывать
    if request.user.is_client:
        deals = Deal.objects.filter(
            client=request.user
        ).select_related('task', 'task__category', 'specialist', 'offer').order_by('-created_at')
        user_role = 'client'
    elif request.user.is_specialist:
        deals = Deal.objects.filter(
            specialist=request.user
        ).select_related('task', 'task__category', 'client', 'offer').order_by('-created_at')
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

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
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
    - language: 'ru' или 'uz' (опционально, по умолчанию 'ru')
    
    Возвращает:
    - suggested_title: предложенный заголовок
    - suggested_category: предложенная категория
    - refined_description: улучшенное описание
    - estimated_budget_min: минимальный бюджет
    - estimated_budget_max: максимальный бюджет
    """
    description = request.data.get('description', '').strip()
    language = request.data.get('language', 'ru')
    
    if not description:
        return Response(
            {'error': 'Описание задачи обязательно'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = analyze_task_description(description, language)
    
    if result:
        return Response(result.to_dict(), status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Не удалось проанализировать задачу. Попробуйте позже.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
