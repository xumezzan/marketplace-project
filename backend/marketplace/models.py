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


class Subcategory(models.Model):
    """
    Модель подкатегории услуг.
    
    Примеры: 'Репетитор по математике', 'Ремонт стиральных машин', 
    'Уборка квартиры', 'Маникюр' и т.д.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='категория',
        help_text="Родительская категория"
    )
    name = models.CharField(
        'название',
        max_length=150,
        help_text="Название подкатегории (например, 'Репетитор по математике')"
    )
    slug = models.SlugField(
        'slug',
        max_length=150,
        unique=True,
        blank=True,
        help_text="URL-friendly версия названия"
    )
    description = models.TextField(
        'описание',
        blank=True,
        null=True,
        help_text="Описание подкатегории"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'subcategories'
        verbose_name = 'подкатегория'
        verbose_name_plural = 'подкатегории'
        ordering = ['category', 'name']
        unique_together = [['category', 'name']]
    
    def __str__(self) -> str:
        return f"{self.category.name} → {self.name}"
    
    def save(self, *args, **kwargs):
        """Автоматически генерирует slug из названия, если не указан."""
        if not self.slug:
            self.slug = slugify(f"{self.category.slug}-{self.name}")
        super().save(*args, **kwargs)


class ClientProfile(models.Model):
    """
    Профиль клиента с предпочтениями и адресом.
    
    Хранит информацию специфичную для клиентов: адрес, предпочитаемые
    специалисты, историю заказов и т.д.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='пользователь',
        help_text="Пользователь, которому принадлежит этот профиль"
    )
    address = models.CharField(
        'адрес',
        max_length=500,
        blank=True,
        null=True,
        help_text="Основной адрес клиента"
    )
    preferences = models.JSONField(
        'предпочтения',
        default=dict,
        blank=True,
        help_text="JSON с предпочтениями клиента (например, {'preferred_time': 'morning', 'languages': ['ru', 'uz']})"
    )
    favorite_specialists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorited_by_clients',
        blank=True,
        verbose_name='избранные специалисты',
        help_text="Список избранных специалистов"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'client_profiles'
        verbose_name = 'профиль клиента'
        verbose_name_plural = 'профили клиентов'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.user.username} - Профиль клиента"



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
    # Новые поля для расписания и зоны обслуживания
    working_days = models.JSONField(
        'рабочие дни',
        default=list,
        blank=True,
        help_text="Список рабочих дней (например, ['mon', 'tue', 'wed', 'thu', 'fri'])"
    )
    working_hours_start = models.TimeField(
        'начало рабочего дня',
        blank=True,
        null=True,
        help_text="Время начала рабочего дня (например, 09:00)"
    )
    working_hours_end = models.TimeField(
        'конец рабочего дня',
        blank=True,
        null=True,
        help_text="Время окончания рабочего дня (например, 18:00)"
    )
    service_radius_km = models.PositiveIntegerField(
        'радиус выезда (км)',
        default=0,
        help_text="Радиус выезда в километрах (0 = не выезжает)"
    )
    works_online = models.BooleanField(
        'работает онлайн',
        default=False,
        help_text="Специалист предоставляет услуги онлайн"
    )
    verification_documents = models.JSONField(
        'документы верификации',
        default=dict,
        blank=True,
        help_text="JSON с информацией о загруженных документах (паспорт, лицензии и т.д.)"
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
    
    class Format(models.TextChoices):
        """Формат выполнения услуги."""
        ONLINE = 'online', 'Онлайн'
        OFFLINE = 'offline', 'Выезд к клиенту'
        AT_SPECIALIST = 'at_specialist', 'У специалиста'
    
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
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.SET_NULL,
        related_name='tasks',
        verbose_name='подкатегория',
        blank=True,
        null=True,
        help_text="Подкатегория услуги (необязательно)"
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
    format = models.CharField(
        'формат',
        max_length=20,
        choices=Format.choices,
        default=Format.OFFLINE,
        help_text="Формат выполнения услуги"
    )
    latitude = models.DecimalField(
        'широта',
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Широта местоположения задачи"
    )
    longitude = models.DecimalField(
        'долгота',
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Долгота местоположения задачи"
    )
    deadline_date = models.DateField(
        'крайний срок',
        blank=True,
        null=True,
        help_text="Дедлайн выполнения задачи (если отличается от preferred_date)"
    )
    auto_structured = models.BooleanField(
        'создано через ИИ',
        default=False,
        help_text="Задача была создана/структурирована с помощью ИИ"
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
        IN_PROGRESS = 'in_progress', 'В работе'  # Оплачено и выполняется
        COMPLETED = 'completed', 'Завершено'
        CANCELED = 'canceled', 'Отменено'
    
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


class TimeSlot(models.Model):
    """
    Модель временного слота в расписании специалиста.
    
    Позволяет специалистам управлять своим временем, а клиентам - бронировать слоты.
    """
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name='специалист'
    )
    date = models.DateField('дата')
    time_start = models.TimeField('время начала')
    time_end = models.TimeField('время окончания')
    is_available = models.BooleanField('свободен', default=True)
    
    # Если слот забронирован под сделку
    deal = models.ForeignKey(
        'Deal',
        on_delete=models.SET_NULL,
        related_name='time_slots',
        verbose_name='сделка',
        null=True,
        blank=True,
        help_text="Сделка, под которую забронирован этот слот"
    )
    
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)

    class Meta:
        db_table = 'time_slots'
        verbose_name = 'временной слот'
        verbose_name_plural = 'временные слоты'
        ordering = ['date', 'time_start']
        unique_together = ['specialist', 'date', 'time_start']
        indexes = [
            models.Index(fields=['specialist', 'date', 'is_available']),
            models.Index(fields=['date', 'is_available']),
        ]

    def __str__(self):
        status = "Свободен" if self.is_available else "Занят"
        return f"{self.specialist.username}: {self.date} {self.time_start}-{self.time_end} ({status})"

class PortfolioItem(models.Model):
    """
    Модель элемента портфолио специалиста.
    
    Специалисты могут загружать изображения своих работ в портфолио.
    """
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_items',
        verbose_name='специалист',
        help_text="Специалист, которому принадлежит это портфолио"
    )
    title = models.CharField(
        'название',
        max_length=200,
        help_text="Название работы"
    )
    description = models.TextField(
        'описание',
        blank=True,
        help_text="Описание работы"
    )
    image = models.ImageField(
        'изображение',
        upload_to='portfolio/%Y/%m/',
        help_text="Изображение работы"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='portfolio_items',
        verbose_name='категория'
    )
    order = models.IntegerField(
        'порядок',
        default=0,
        help_text="Порядок отображения (меньше - выше)"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'portfolio_items'
        verbose_name = 'элемент портфолио'
        verbose_name_plural = 'портфолио'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.specialist.username})"


class Availability(models.Model):
    """
    Расписание доступности специалиста (повторяющееся).
    Например: Понедельник 09:00 - 18:00.
    """
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availability_slots',
        verbose_name='специалист'
    )
    day_of_week = models.IntegerField(
        'день недели',
        choices=[
            (0, 'Понедельник'), (1, 'Вторник'), (2, 'Среда'),
            (3, 'Четверг'), (4, 'Пятница'), (5, 'Суббота'), (6, 'Воскресенье')
        ],
        help_text="День недели (0 - Понедельник, 6 - Воскресенье)"
    )
    start_time = models.TimeField('время начала')
    end_time = models.TimeField('время окончания')
    is_recurring = models.BooleanField('повторяющееся', default=True)
    
    class Meta:
        db_table = 'availability_slots'
        verbose_name = 'слот доступности'
        verbose_name_plural = 'слоты доступности'
        ordering = ['day_of_week', 'start_time']
        unique_together = ['specialist', 'day_of_week', 'start_time']
    
    def __str__(self):
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        return f"{self.specialist.username}: {days[self.day_of_week]} {self.start_time}-{self.end_time}"


class Booking(models.Model):
    """
    Бронирование услуги на конкретную дату и время.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждено'
        CANCELLED = 'cancelled', 'Отменено'
        COMPLETED = 'completed', 'Завершено'
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='задача'
    )
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings_as_specialist',
        verbose_name='специалист'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings_as_client',
        verbose_name='клиент'
    )
    
    scheduled_date = models.DateField('дата')
    scheduled_time = models.TimeField('время')
    duration_minutes = models.IntegerField('длительность (мин)', default=60)
    
    status = models.CharField(
        'статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    notes = models.TextField('примечания', blank=True)
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        verbose_name = 'бронирование'
        verbose_name_plural = 'бронирования'
        ordering = ['-scheduled_date', '-scheduled_time']
        indexes = [
            models.Index(fields=['specialist', 'scheduled_date']),
            models.Index(fields=['client', 'status']),
        ]
    
    def __str__(self):
        return f"Бронирование: {self.task.title} - {self.scheduled_date} {self.scheduled_time}"


class Escrow(models.Model):
    """
    Модель escrow (резервирование средств) для безопасных сделок.
    
    Средства резервируются на счете и переводятся исполнителю
    только после подтверждения выполнения работы клиентом.
    """
    
    class Status(models.TextChoices):
        """Статусы escrow."""
        PENDING = 'pending', 'Ожидает резервирования'
        RESERVED = 'reserved', 'Средства зарезервированы'
        LOCKED = 'locked', 'Средства заблокированы'
        RELEASED = 'released', 'Средства переведены'
        REFUNDED = 'refunded', 'Средства возвращены'
    
    deal = models.OneToOneField(
        Deal,
        on_delete=models.CASCADE,
        related_name='escrow',
        verbose_name='сделка',
        help_text="Сделка, для которой создан escrow"
    )
    amount = models.DecimalField(
        'сумма',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Сумма для резервирования"
    )
    status = models.CharField(
        'статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Текущий статус escrow"
    )
    reserved_at = models.DateTimeField(
        'дата резервирования',
        blank=True,
        null=True,
        help_text="Когда средства были зарезервированы"
    )
    released_at = models.DateTimeField(
        'дата перевода',
        blank=True,
        null=True,
        help_text="Когда средства были переведены исполнителю"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'escrows'
        verbose_name = 'escrow'
        verbose_name_plural = 'escrows'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Escrow для сделки {self.deal.id} - {self.amount} ({self.get_status_display()})"
    
    def reserve(self) -> None:
        """Резервирует средства."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.RESERVED
            from django.utils import timezone
            self.reserved_at = timezone.now()
            self.save()
    
    def lock(self) -> None:
        """Блокирует средства (работа начата)."""
        if self.status == self.Status.RESERVED:
            self.status = self.Status.LOCKED
            self.save()
    
    def release(self) -> None:
        """Переводит средства исполнителю."""
        if self.status == self.Status.LOCKED:
            self.status = self.Status.RELEASED
            from django.utils import timezone
            self.released_at = timezone.now()
            self.save()
    
    def refund(self) -> None:
        """Возвращает средства клиенту."""
        if self.status in [self.Status.RESERVED, self.Status.LOCKED]:
            self.status = self.Status.REFUNDED
            self.save()


class AIRequest(models.Model):
    """
    Модель для логирования AI запросов.
    
    Сохраняет все запросы к AI сервису для анализа и отладки.
    """
    
    class RequestType(models.TextChoices):
        """Типы AI запросов."""
        PARSE = 'parse', 'Парсинг текста'
        ESTIMATE = 'estimate', 'Оценка стоимости'
        RANK = 'rank', 'Ранжирование'
        SCHEDULE = 'schedule', 'Подбор расписания'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='ai_requests',
        verbose_name='пользователь',
        blank=True,
        null=True,
        help_text="Пользователь, сделавший запрос"
    )
    request_type = models.CharField(
        'тип запроса',
        max_length=20,
        choices=RequestType.choices,
        help_text="Тип AI запроса"
    )
    input_data = models.JSONField(
        'входные данные',
        help_text="JSON с входными данными запроса"
    )
    output_data = models.JSONField(
        'выходные данные',
        default=dict,
        blank=True,
        help_text="JSON с результатом AI обработки"
    )
    model_used = models.CharField(
        'модель',
        max_length=50,
        default='gemini-1.5-flash',
        help_text="Название использованной AI модели"
    )
    success = models.BooleanField(
        'успешно',
        default=True,
        help_text="Успешно ли выполнен запрос"
    )
    error_message = models.TextField(
        'сообщение об ошибке',
        blank=True,
        null=True,
        help_text="Сообщение об ошибке если запрос не удался"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    
    class Meta:
        db_table = 'ai_requests'
        verbose_name = 'AI запрос'
        verbose_name_plural = 'AI запросы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self) -> str:
        user_str = self.user.username if self.user else 'Анонимный'
        return f"{self.get_request_type_display()} - {user_str} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class Conversation(models.Model):
    """
    Модель для хранения переписки между двумя пользователями.
    """
    from django.conf import settings
    
    participant1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_participant1',
        verbose_name='участник 1'
    )
    participant2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_participant2',
        verbose_name='участник 2'
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        verbose_name = 'переписка'
        verbose_name_plural = 'переписки'
        ordering = ['-updated_at']
        unique_together = [['participant1', 'participant2']]
        indexes = [
            models.Index(fields=['participant1', 'participant2']),
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        return f"Conversation between {self.participant1.username} and {self.participant2.username}"
    
    def get_other_participant(self, user):
        """Возвращает другого участника переписки."""
        return self.participant2 if self.participant1 == user else self.participant1
    
    def get_last_message(self):
        """Возвращает последнее сообщение в переписке."""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, user):
        """Возвращает количество непрочитанных сообщений для пользователя."""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """
    Модель для хранения отдельного сообщения в переписке.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='переписка'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='marketplace_sent_messages',
        verbose_name='отправитель'
    )
    content = models.TextField('содержание')
    is_read = models.BooleanField('прочитано', default=False)
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender} in {self.conversation}"


class Notification(models.Model):
    """
    Model for user notifications.
    """
    class Type(models.TextChoices):
        BOOKING = 'booking', 'Бронирование'
        MESSAGE = 'message', 'Сообщение'
        SYSTEM = 'system', 'Система'
        REVIEW = 'review', 'Отзыв'
        
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marketplace_notifications')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.type}: {self.title} ({self.user})"


class NotificationPreference(models.Model):
    """
    User notification preferences.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    email_booking = models.BooleanField(default=True)
    email_message = models.BooleanField(default=True)
    email_review = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Preferences for {self.user}"


class Favorite(models.Model):
    """
    Model for storing user's favorite specialists.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'specialist')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user} favorites {self.specialist}"
