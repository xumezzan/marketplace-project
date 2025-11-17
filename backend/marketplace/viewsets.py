"""
ViewSet'ы для marketplace API.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import models
from .models import Category, Task, Offer, Review, Deal
from .serializers import (
    CategorySerializer, TaskSerializer, OfferSerializer,
    UserSerializer, ReviewSerializer, DealSerializer
)

User = get_user_model()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для категорий.
    
    Только чтение (list, retrieve) для всех пользователей.
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # Доступно всем
    lookup_field = 'slug'  # Поиск по slug вместо id


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для задач.
    
    - list, retrieve: доступно всем
    - create: только авторизованным клиентам
    - update, partial_update, destroy: только владельцу задачи
    """
    queryset = Task.objects.select_related('client', 'category').prefetch_related('offers').all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Фильтрация задач по статусу и другим параметрам."""
        queryset = super().get_queryset()
        
        # Фильтр по статусу
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Фильтр по категории
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Фильтр по городу
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Фильтр по клиенту (для получения задач конкретного пользователя)
        client = self.request.query_params.get('client', None)
        if client:
            queryset = queryset.filter(client_id=client)
        
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        """Настройка прав доступа в зависимости от действия."""
        if self.action == 'create':
            # Создание только для авторизованных клиентов
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактирование только для владельца
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Создание задачи от имени текущего пользователя."""
        # Проверка роли клиента выполняется в сериализаторе
        serializer.save()
    
    def perform_update(self, serializer):
        """Обновление задачи с проверкой прав."""
        task = self.get_object()
        
        # Проверяем, что пользователь является владельцем задачи
        if self.request.user != task.client:
            raise permissions.PermissionDenied(
                'Вы можете редактировать только свои задачи.'
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Удаление задачи с проверкой прав."""
        # Проверяем, что пользователь является владельцем задачи
        if self.request.user != instance.client:
            raise permissions.PermissionDenied(
                'Вы можете удалять только свои задачи.'
            )
        
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        """Опубликовать задачу (изменить статус на PUBLISHED)."""
        task = self.get_object()
        
        # Проверяем права
        if request.user != task.client:
            return Response(
                {'error': 'Вы можете публиковать только свои задачи.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем, что задача в статусе DRAFT
        if task.status != Task.Status.DRAFT:
            return Response(
                {'error': f'Задачу со статусом "{task.get_status_display()}" нельзя опубликовать.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = Task.Status.PUBLISHED
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet для предложений.
    
    - list, retrieve: доступно всем авторизованным
    - create: только авторизованным специалистам
    - update, partial_update, destroy: только автору предложения
    """
    queryset = Offer.objects.select_related('task', 'specialist').all()
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Фильтрация предложений."""
        queryset = super().get_queryset()
        
        # Фильтр по задаче
        task = self.request.query_params.get('task', None)
        if task:
            queryset = queryset.filter(task_id=task)
        
        # Фильтр по специалисту
        specialist = self.request.query_params.get('specialist', None)
        if specialist:
            queryset = queryset.filter(specialist_id=specialist)
        
        # Фильтр по статусу
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        """Настройка прав доступа в зависимости от действия."""
        if self.action == 'create':
            # Создание только для авторизованных специалистов
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактирование только для автора предложения
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Создание предложения от имени текущего пользователя."""
        # Проверка роли специалиста выполняется в сериализаторе
        serializer.save()
    
    def perform_update(self, serializer):
        """Обновление предложения с проверкой прав."""
        offer = self.get_object()
        
        # Проверяем, что пользователь является автором предложения
        if self.request.user != offer.specialist:
            raise permissions.PermissionDenied(
                'Вы можете редактировать только свои предложения.'
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Удаление предложения с проверкой прав."""
        # Проверяем, что пользователь является автором предложения
        if self.request.user != instance.specialist:
            raise permissions.PermissionDenied(
                'Вы можете удалять только свои предложения.'
            )
        
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        """Принять предложение (только владелец задачи)."""
        offer = self.get_object()
        task = offer.task
        
        # Проверяем, что пользователь является владельцем задачи
        if request.user != task.client:
            return Response(
                {'error': 'Только владелец задачи может принимать предложения.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем, что предложение можно принять
        if not offer.can_be_accepted():
            return Response(
                {'error': 'Это предложение нельзя принять.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Принимаем предложение
        offer.accept()
        
        serializer = self.get_serializer(offer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        """Отклонить предложение (только владелец задачи)."""
        offer = self.get_object()
        task = offer.task
        
        # Проверяем, что пользователь является владельцем задачи
        if request.user != task.client:
            return Response(
                {'error': 'Только владелец задачи может отклонять предложения.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем, что предложение можно отклонить
        if offer.status != Offer.Status.PENDING:
            return Response(
                {'error': 'Можно отклонить только предложения со статусом "Ожидает".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Отклоняем предложение
        offer.reject()
        
        serializer = self.get_serializer(offer)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для пользователей.
    
    Только чтение (list, retrieve) для авторизованных пользователей.
    Пользователь может видеть только свой профиль полностью, остальных - ограниченно.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Фильтрация пользователей."""
        queryset = super().get_queryset()
        
        # Фильтр по роли
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        # Фильтр по городу
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        return queryset.order_by('-date_joined')
    
    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action == 'retrieve' and self.request.user == self.get_object():
            # Для своего профиля показываем полную информацию
            return UserSerializer
        return UserSerializer  # Можно создать UserPublicSerializer для ограниченного доступа


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для отзывов.
    
    - list, retrieve: доступно всем авторизованным
    - create: только авторизованным клиентам
    - update, partial_update, destroy: только автору отзыва
    """
    queryset = Review.objects.select_related('specialist', 'client', 'task').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Фильтрация отзывов."""
        queryset = super().get_queryset()
        
        # Фильтр по специалисту
        specialist = self.request.query_params.get('specialist', None)
        if specialist:
            queryset = queryset.filter(specialist_id=specialist)
        
        # Фильтр по клиенту
        client = self.request.query_params.get('client', None)
        if client:
            queryset = queryset.filter(client_id=client)
        
        # Фильтр по задаче
        task = self.request.query_params.get('task', None)
        if task:
            queryset = queryset.filter(task_id=task)
        
        # Фильтр по рейтингу
        rating = self.request.query_params.get('rating', None)
        if rating:
            queryset = queryset.filter(rating=rating)
        
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        """Настройка прав доступа в зависимости от действия."""
        if self.action == 'create':
            # Создание только для авторизованных клиентов
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактирование только для автора отзыва
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Создание отзыва от имени текущего пользователя."""
        # Проверка роли клиента выполняется в сериализаторе
        serializer.save()
    
    def perform_update(self, serializer):
        """Обновление отзыва с проверкой прав."""
        review = self.get_object()
        
        # Проверяем, что пользователь является автором отзыва
        if self.request.user != review.client:
            raise permissions.PermissionDenied(
                'Вы можете редактировать только свои отзывы.'
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Удаление отзыва с проверкой прав."""
        # Проверяем, что пользователь является автором отзыва
        if self.request.user != instance.client:
            raise permissions.PermissionDenied(
                'Вы можете удалять только свои отзывы.'
            )
        
        instance.delete()


class DealViewSet(viewsets.ModelViewSet):
    """
    ViewSet для сделок.
    
    - list, retrieve: доступно авторизованным (только свои сделки)
    - create: только авторизованным клиентам (через принятие оффера)
    - update, partial_update: только участникам сделки
    - destroy: недоступно (сделки не удаляются)
    """
    queryset = Deal.objects.select_related('task', 'offer', 'client', 'specialist').all()
    serializer_class = DealSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Фильтрация сделок (показываем только свои)."""
        queryset = super().get_queryset()
        
        # Показываем только сделки, где пользователь является клиентом или специалистом
        queryset = queryset.filter(
            models.Q(client=self.request.user) | models.Q(specialist=self.request.user)
        )
        
        # Фильтр по статусу
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Фильтр по задаче
        task = self.request.query_params.get('task', None)
        if task:
            queryset = queryset.filter(task_id=task)
        
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        """Настройка прав доступа в зависимости от действия."""
        if self.action == 'create':
            # Создание только для авторизованных клиентов
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            # Редактирование только для участников сделки
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            # Удаление недоступно
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Создание сделки от имени текущего пользователя."""
        # Проверка роли клиента и бизнес-логика выполняется в сериализаторе
        serializer.save()
    
    def perform_update(self, serializer):
        """Обновление сделки с проверкой прав."""
        deal = self.get_object()
        
        # Проверяем, что пользователь является участником сделки
        if self.request.user != deal.client and self.request.user != deal.specialist:
            raise permissions.PermissionDenied(
                'Вы можете редактировать только свои сделки.'
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Удаление сделки запрещено."""
        raise permissions.PermissionDenied(
            'Удаление сделок недоступно.'
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_paid(self, request, pk=None):
        """Отметить сделку как оплаченную."""
        deal = self.get_object()
        
        # Проверяем права
        if request.user != deal.client and request.user != deal.specialist:
            return Response(
                {'error': 'Только участники сделки могут изменять её статус.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем текущий статус
        if deal.status != Deal.Status.PENDING_PAYMENT:
            return Response(
                {'error': f'Сделку со статусом "{deal.get_status_display()}" нельзя отметить как оплаченную.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deal.mark_as_paid()
        
        serializer = self.get_serializer(deal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_completed(self, request, pk=None):
        """Отметить сделку как завершенную."""
        deal = self.get_object()
        
        # Проверяем права
        if request.user != deal.client and request.user != deal.specialist:
            return Response(
                {'error': 'Только участники сделки могут изменять её статус.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем текущий статус
        if deal.status not in [Deal.Status.PAID, Deal.Status.PENDING_PAYMENT]:
            return Response(
                {'error': f'Сделку со статусом "{deal.get_status_display()}" нельзя отметить как завершенную.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deal.mark_as_completed()
        
        serializer = self.get_serializer(deal)
        return Response(serializer.data)

