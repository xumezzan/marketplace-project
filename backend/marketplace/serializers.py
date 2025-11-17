"""
Сериализаторы для marketplace API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Task, Offer, Review, Deal

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Task."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    client_username = serializers.CharField(source='client.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    budget_display = serializers.CharField(source='budget_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id',
            'client',
            'client_username',
            'category',
            'category_name',
            'title',
            'description',
            'budget_min',
            'budget_max',
            'budget_display',
            'address',
            'city',
            'preferred_date',
            'preferred_time',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'client', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Создает задачу от имени текущего пользователя."""
        # Получаем пользователя из контекста запроса
        user = self.context['request'].user
        
        # Проверяем, что пользователь является клиентом
        if not user.is_client:
            raise serializers.ValidationError(
                'Только клиенты могут создавать задачи.'
            )
        
        # Устанавливаем клиента и статус по умолчанию
        validated_data['client'] = user
        validated_data['status'] = Task.Status.DRAFT
        
        return super().create(validated_data)


class OfferSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Offer."""
    
    specialist_username = serializers.CharField(source='specialist.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Offer
        fields = [
            'id',
            'task',
            'task_title',
            'specialist',
            'specialist_username',
            'proposed_price',
            'message',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'specialist', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Создает предложение от имени текущего пользователя."""
        # Получаем пользователя из контекста запроса
        user = self.context['request'].user
        
        # Проверяем, что пользователь является специалистом
        if not user.is_specialist:
            raise serializers.ValidationError(
                'Только специалисты могут создавать предложения.'
            )
        
        # Получаем задачу
        task = validated_data.get('task')
        
        # Проверяем, может ли задача принимать предложения
        if not task.can_receive_offers():
            raise serializers.ValidationError(
                'Эта задача больше не принимает предложения.'
            )
        
        # Проверяем, нет ли уже предложения от этого специалиста
        if Offer.objects.filter(task=task, specialist=user).exists():
            raise serializers.ValidationError(
                'Вы уже отправили предложение по этой задаче.'
            )
        
        # Устанавливаем специалиста и статус по умолчанию
        validated_data['specialist'] = user
        validated_data['status'] = Offer.Status.PENDING
        
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'role_display',
            'phone',
            'city',
            'rating',
            'reviews_count',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'rating']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get_reviews_count(self, obj):
        """Возвращает количество отзывов для специалиста."""
        if obj.is_specialist:
            return Review.objects.filter(specialist=obj).count()
        return 0


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    
    specialist_username = serializers.CharField(source='specialist.username', read_only=True)
    client_username = serializers.CharField(source='client.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id',
            'specialist',
            'specialist_username',
            'client',
            'client_username',
            'task',
            'task_title',
            'rating',
            'text',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'client', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Создает отзыв от имени текущего пользователя."""
        # Получаем пользователя из контекста запроса
        user = self.context['request'].user
        
        # Проверяем, что пользователь является клиентом
        if not user.is_client:
            raise serializers.ValidationError(
                'Только клиенты могут оставлять отзывы.'
            )
        
        # Получаем задачу
        task = validated_data.get('task')
        
        # Проверяем, что пользователь является владельцем задачи
        if task.client != user:
            raise serializers.ValidationError(
                'Вы можете оставлять отзывы только по своим задачам.'
            )
        
        # Проверяем, что задача завершена
        if task.status != Task.Status.COMPLETED:
            raise serializers.ValidationError(
                'Отзыв можно оставить только по завершенной задаче.'
            )
        
        # Проверяем, нет ли уже отзыва от этого клиента по этой задаче
        if Review.objects.filter(task=task, client=user).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв по этой задаче.'
            )
        
        # Устанавливаем клиента и специалиста из задачи
        validated_data['client'] = user
        # Специалист берется из принятого оффера задачи
        try:
            accepted_offer = Offer.objects.get(task=task, status=Offer.Status.ACCEPTED)
            validated_data['specialist'] = accepted_offer.specialist
        except Offer.DoesNotExist:
            raise serializers.ValidationError(
                'Не найдено принятое предложение по этой задаче.'
            )
        
        return super().create(validated_data)


class DealSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Deal."""
    
    task_title = serializers.CharField(source='task.title', read_only=True)
    client_username = serializers.CharField(source='client.username', read_only=True)
    specialist_username = serializers.CharField(source='specialist.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Deal
        fields = [
            'id',
            'task',
            'task_title',
            'offer',
            'client',
            'client_username',
            'specialist',
            'specialist_username',
            'final_price',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'client', 'specialist', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Создание сделки через API (обычно создается при принятии оффера)."""
        # Получаем пользователя из контекста запроса
        user = self.context['request'].user
        
        # Проверяем, что пользователь является клиентом
        if not user.is_client:
            raise serializers.ValidationError(
                'Только клиенты могут создавать сделки.'
            )
        
        # Получаем оффер
        offer = validated_data.get('offer')
        task = offer.task
        
        # Проверяем, что пользователь является владельцем задачи
        if task.client != user:
            raise serializers.ValidationError(
                'Вы можете создавать сделки только по своим задачам.'
            )
        
        # Проверяем, можно ли принять оффер
        if not offer.can_be_accepted():
            raise serializers.ValidationError(
                'Это предложение нельзя принять.'
            )
        
        # Проверяем, нет ли уже сделки для этой задачи
        if Deal.objects.filter(task=task).exists():
            raise serializers.ValidationError(
                'По этой задаче уже создана сделка.'
            )
        
        # Устанавливаем клиента, специалиста и финальную цену
        validated_data['client'] = user
        validated_data['specialist'] = offer.specialist
        validated_data['final_price'] = offer.proposed_price
        validated_data['status'] = Deal.Status.PENDING_PAYMENT
        
        # Принимаем оффер (обновит статусы)
        offer.accept()
        
        return super().create(validated_data)

