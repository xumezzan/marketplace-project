"""
Кастомная модель User для marketplace приложения.

Расширяет Django AbstractUser для добавления ролей и полей,
специфичных для marketplace.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями CLIENT и SPECIALIST.
    
    Расширяет AbstractUser следующими полями:
    - role: роль пользователя (клиент или специалист)
    - phone: телефонный номер
    - city: город пользователя
    - rating: средний рейтинг (0.00 - 5.00)
    - is_client: флаг клиента
    - is_specialist: флаг специалиста
    """
    
    # Email делаем обязательным и уникальным
    email = models.EmailField(
        'email адрес',
        unique=True,
        help_text="Email адрес пользователя (обязательное поле)"
    )
    
    # Роли пользователя (может быть и клиентом, и специалистом одновременно)
    is_client = models.BooleanField(
        'клиент',
        default=True,
        help_text="Пользователь является клиентом"
    )
    is_specialist = models.BooleanField(
        'специалист',
        default=False,
        help_text="Пользователь является специалистом"
    )
    
    # Телефон
    phone = models.CharField(
        'телефон',
        max_length=20,
        blank=True,
        null=True,
        help_text="Номер телефона пользователя"
    )
    
    # Город
    city = models.CharField(
        'город',
        max_length=100,
        blank=True,
        null=True,
        help_text="Город пользователя"
    )
    
    # Рейтинг (средний)
    rating = models.DecimalField(
        'рейтинг',
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[
            MinValueValidator(0.00),
            MaxValueValidator(5.00)
        ],
        help_text="Средний рейтинг пользователя (от 0.00 до 5.00)"
    )
    
    # Аватар
    avatar = models.ImageField(
        'аватар',
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Фото профиля пользователя"
    )
    
    # Временные метки
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        """Строковое представление пользователя."""
        roles = []
        if self.is_client:
            roles.append('Клиент')
        if self.is_specialist:
            roles.append('Специалист')
        role_str = ', '.join(roles) if roles else 'Нет ролей'
        return f"{self.username} ({role_str})"
    
    def get_role_display(self) -> str:
        """Возвращает текстовое представление ролей для обратной совместимости."""
        roles = []
        if self.is_client:
            roles.append('Клиент')
        if self.is_specialist:
            roles.append('Специалист')
        return ', '.join(roles) if roles else 'Нет ролей'
