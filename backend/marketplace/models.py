"""
Модели для marketplace приложения.

Содержит модели: Category, SpecialistProfile, Task, Offer, Review, Deal.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models import Avg


class Category(models.Model):
    """
    Модель категории услуг.
    
    Примеры: Ремонт, Репетитор, Фитнес-тренер, Мастер красоты и т.д.
    """
    name = models.CharField(
        'название',
        max_length=100,
        unique=True,
        help_text="Название категории (например, 'Ремонт', 'Репетитор')"
    )
    slug = models.SlugField(
        'slug',
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly версия названия"
    )
    description = models.TextField(
        'описание',
        blank=True,
        null=True,
        help_text="Описание категории"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        """Автоматически генерирует slug из названия, если не указан."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SpecialistProfile(models.Model):
    """
    Профиль специалиста с категориями, опытом, тарифами и статусом верификации.
    
    Каждый специалист может иметь несколько категорий и детальный профиль.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='specialist_profile',
        verbose_name='пользователь',
        help_text="Пользователь, которому принадлежит этот профиль"
    )
    categories = models.ManyToManyField(
        Category,
        related_name='specialists',
        blank=True,
        verbose_name='категории',
        help_text="Категории услуг, которые предоставляет специалист"
    )
    description = models.TextField(
        'описание',
        blank=True,
        null=True,
        help_text="Биография/описание специалиста"
    )
    years_of_experience = models.PositiveIntegerField(
        'лет опыта',
        default=0,
        help_text="Количество лет опыта в сфере"
    )
    hourly_rate = models.DecimalField(
        'почасовая ставка',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Почасовая ставка в местной валюте"
    )
    typical_price_range_min = models.DecimalField(
        'минимальная цена',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Минимальная типичная цена"
    )
    typical_price_range_max = models.DecimalField(
        'максимальная цена',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Максимальная типичная цена"
    )
    is_verified = models.BooleanField(
        'верифицирован',
        default=False,
        help_text="Верифицирован ли специалист администратором"
    )
    portfolio_links = models.JSONField(
        'ссылки на портфолио',
        default=list,
        blank=True,
        help_text="Список URL портфолио (например, ['https://example.com/portfolio'])"
    )
    active = models.BooleanField(
        'активен',
        default=True,
        help_text="Активен ли специалист в данный момент"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'specialist_profiles'
        verbose_name = 'профиль специалиста'
        verbose_name_plural = 'профили специалистов'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.user.username} - Профиль специалиста"
    
    @property
    def price_range_display(self) -> str:
        """Возвращает отформатированную строку диапазона цен."""
        if self.typical_price_range_min and self.typical_price_range_max:
            return f"{self.typical_price_range_min} - {self.typical_price_range_max}"
        elif self.hourly_rate:
            return f"{self.hourly_rate}/час"
        return "Не указано"


class Task(models.Model):
    """
    Модель задачи, представляющая запрос клиента на услугу.
    
    Клиенты создают задачи с деталями: категория, описание, бюджет,
    местоположение и предпочтительное время. Специалисты могут затем
    ответить предложениями.
    """
    
    class Status(models.TextChoices):
        """Статусы задачи."""
        DRAFT = 'draft', 'Черновик'
        PUBLISHED = 'published', 'Опубликовано'
        IN_PROGRESS = 'in_progress', 'В работе'
        COMPLETED = 'completed', 'Завершено'
        CANCELLED = 'cancelled', 'Отменено'
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='клиент',
        help_text="Клиент, создавший эту задачу"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='tasks',
        verbose_name='категория',
        help_text="Категория услуги для этой задачи"
    )
    title = models.CharField(
        'заголовок',
        max_length=200,
        help_text="Заголовок/краткое описание задачи"
    )
    description = models.TextField(
        'описание',
        help_text="Подробное описание задачи"
    )
    budget_min = models.DecimalField(
        'минимальный бюджет',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Минимальный бюджет"
    )
    budget_max = models.DecimalField(
        'максимальный бюджет',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Максимальный бюджет"
    )
    address = models.CharField(
        'адрес',
        max_length=500,
        blank=True,
        null=True,
        help_text="Полный адрес или текст местоположения"
    )
    city = models.CharField(
        'город',
        max_length=100,
        help_text="Город, где должна быть выполнена задача"
    )
    preferred_date = models.DateField(
        'предпочтительная дата',
        blank=True,
        null=True,
        help_text="Предпочтительная дата выполнения услуги"
    )
    preferred_time = models.TimeField(
        'предпочтительное время',
        blank=True,
        null=True,
        help_text="Предпочтительное время выполнения услуги"
    )
    status = models.CharField(
        'статус',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text="Текущий статус задачи"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'задача'
        verbose_name_plural = 'задачи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'city']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self) -> str:
        return f"{self.title} - {self.client.username}"
    
    @property
    def budget_display(self) -> str:
        """Возвращает отформатированную строку бюджета."""
        if self.budget_min and self.budget_max:
            return f"{self.budget_min} - {self.budget_max}"
        elif self.budget_min:
            return f"От {self.budget_min}"
        elif self.budget_max:
            return f"До {self.budget_max}"
        return "Бюджет не указан"
    
    def can_be_edited(self) -> bool:
        """Проверяет, можно ли еще редактировать задачу (только черновик или опубликовано)."""
        return self.status in [self.Status.DRAFT, self.Status.PUBLISHED]
    
    def can_receive_offers(self) -> bool:
        """Проверяет, может ли задача получать новые предложения."""
        return self.status == self.Status.PUBLISHED


class Offer(models.Model):
    """
    Модель предложения, представляющая ответ специалиста на задачу.
    
    Специалисты создают предложения с предложенной ценой и сообщением.
    Клиенты могут принять или отклонить предложения.
    """
    
    class Status(models.TextChoices):
        """Статусы предложения."""
        PENDING = 'pending', 'Ожидает'
        ACCEPTED = 'accepted', 'Принято'
        REJECTED = 'rejected', 'Отклонено'
        CANCELLED = 'cancelled', 'Отменено'
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name='задача',
        help_text="Задача, для которой это предложение"
    )
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name='специалист',
        help_text="Специалист, делающий это предложение"
    )
    proposed_price = models.DecimalField(
        'предложенная цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Цена, предложенная специалистом"
    )
    message = models.TextField(
        'сообщение',
        help_text="Сообщение от специалиста клиенту"
    )
    status = models.CharField(
        'статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Текущий статус предложения"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'offers'
        verbose_name = 'предложение'
        verbose_name_plural = 'предложения'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['specialist', 'status']),
        ]
        # Предотвращает дублирование предложений от одного специалиста для одной задачи
        unique_together = [['task', 'specialist']]
    
    def __str__(self) -> str:
        return f"Предложение от {self.specialist.username} для {self.task.title} - {self.proposed_price}"
    
    def can_be_accepted(self) -> bool:
        """Проверяет, может ли предложение быть принято (должно быть pending и задача опубликована)."""
        return (
            self.status == self.Status.PENDING and
            self.task.status == self.task.Status.PUBLISHED
        )
    
    def accept(self) -> None:
        """Принимает предложение и обновляет статус связанной задачи."""
        if self.can_be_accepted():
            self.status = self.Status.ACCEPTED
            self.save()
            # Обновляем статус задачи на in_progress
            self.task.status = self.task.Status.IN_PROGRESS
            self.task.save()
            # Отклоняем все остальные pending предложения для этой задачи
            Offer.objects.filter(
                task=self.task,
                status=self.Status.PENDING
            ).exclude(id=self.id).update(status=self.Status.REJECTED)
    
    def reject(self) -> None:
        """Отклоняет предложение."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.REJECTED
            self.save()


class Review(models.Model):
    """
    Модель отзыва клиента о специалисте.
    
    Клиент оставляет отзыв после завершенной задачи.
    Рейтинг специалиста автоматически пересчитывается при добавлении отзыва.
    """
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name='специалист',
        help_text="Специалист, которому оставлен отзыв"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        verbose_name='клиент',
        help_text="Клиент, оставивший отзыв"
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='задача',
        help_text="Задача, по которой оставлен отзыв"
    )
    rating = models.PositiveIntegerField(
        'рейтинг',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Оценка от 1 до 5"
    )
    text = models.TextField(
        'текст отзыва',
        blank=True,
        null=True,
        help_text="Текст отзыва (необязательно)"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        ordering = ['-created_at']
        # Один отзыв от клиента для пары (task, specialist)
        unique_together = [['task', 'specialist', 'client']]
        indexes = [
            models.Index(fields=['specialist', 'rating']),
            models.Index(fields=['task']),
        ]
    
    def __str__(self) -> str:
        return f"Отзыв от {self.client.username} для {self.specialist.username} - {self.rating}/5"
    
    def save(self, *args, **kwargs):
        """Пересчитывает рейтинг специалиста при сохранении отзыва."""
        super().save(*args, **kwargs)
        self._update_specialist_rating()
    
    def delete(self, *args, **kwargs):
        """Пересчитывает рейтинг специалиста при удалении отзыва."""
        specialist = self.specialist
        super().delete(*args, **kwargs)
        self._update_specialist_rating_for_user(specialist)
    
    def _update_specialist_rating(self):
        """Пересчитывает средний рейтинг специалиста."""
        self._update_specialist_rating_for_user(self.specialist)
    
    @staticmethod
    def _update_specialist_rating_for_user(specialist):
        """Пересчитывает средний рейтинг для указанного специалиста."""
        avg_rating = Review.objects.filter(specialist=specialist).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        
        if avg_rating is not None:
            specialist.rating = round(avg_rating, 2)
        else:
            specialist.rating = 0.00
        
        specialist.save(update_fields=['rating'])


class Deal(models.Model):
    """
    Модель сделки между клиентом и специалистом.
    
    Создается после принятия оффера клиентом.
    Отслеживает статус оплаты и выполнения работы.
    """
    
    class Status(models.TextChoices):
        """Статусы сделки."""
        PENDING = 'pending', 'Ожидает оплаты'
        PAID = 'paid', 'Оплачено'
        COMPLETED = 'completed', 'Завершено'
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='deals',
        verbose_name='задача',
        help_text="Задача, по которой создана сделка"
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.PROTECT,
        related_name='deals',
        verbose_name='предложение',
        help_text="Принятое предложение"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_deals',
        verbose_name='клиент',
        help_text="Клиент в сделке"
    )
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='specialist_deals',
        verbose_name='специалист',
        help_text="Специалист в сделке"
    )
    final_price = models.IntegerField(
        'финальная цена',
        validators=[MinValueValidator(0)],
        help_text="Финальная согласованная цена"
    )
    status = models.CharField(
        'статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Текущий статус сделки"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'deals'
        verbose_name = 'сделка'
        verbose_name_plural = 'сделки'
        ordering = ['-created_at']
        # Одна сделка на задачу
        constraints = [
            models.UniqueConstraint(
                fields=['task'],
                name='unique_deal_per_task'
            ),
        ]
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['specialist', 'status']),
        ]
    
    def __str__(self) -> str:
        return f"Сделка: {self.task.title} - {self.final_price} ({self.get_status_display()})"
    
    def mark_as_paid(self) -> None:
        """Отмечает сделку как оплаченную."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.PAID
            self.save()
    
    def mark_as_completed(self) -> None:
        """Отмечает сделку как завершенную."""
        if self.status in [self.Status.PAID, self.Status.PENDING]:
            self.status = self.Status.COMPLETED
            self.save()
            # Также обновляем статус задачи
            self.task.status = self.task.Status.COMPLETED
            self.task.save()
