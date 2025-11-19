"""
Формы для marketplace приложения.
"""
from django import forms
from .models import Task, Category, Offer, Review, PortfolioItem


class TaskCreateForm(forms.ModelForm):
    """
    Форма для создания задачи клиентом.
    
    Автоматически устанавливает клиента и статус DRAFT при создании.
    """
    
    class Meta:
        model = Task
        fields = [
            'category',
            'title',
            'description',
            'budget_min',
            'budget_max',
            'address',
            'city',
            'preferred_date',
            'preferred_time',
        ]
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткое описание задачи',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Подробное описание задачи',
                'required': True,
            }),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Минимальный бюджет',
                'step': '0.01',
                'min': '0',
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Максимальный бюджет',
                'step': '0.01',
                'min': '0',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Полный адрес (необязательно)',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город',
                'required': True,
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'preferred_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
        }
        labels = {
            'category': 'Категория',
            'title': 'Заголовок',
            'description': 'Описание',
            'budget_min': 'Минимальный бюджет',
            'budget_max': 'Максимальный бюджет',
            'address': 'Адрес',
            'city': 'Город',
            'preferred_date': 'Предпочтительная дата',
            'preferred_time': 'Предпочтительное время',
        }
        help_texts = {
            'budget_min': 'Минимальная сумма, которую вы готовы заплатить',
            'budget_max': 'Максимальная сумма, которую вы готовы заплатить',
            'preferred_date': 'Когда вы хотели бы выполнить задачу',
            'preferred_time': 'В какое время (необязательно)',
        }
    
    def __init__(self, *args, **kwargs):
        """Инициализация формы с улучшенным отображением категорий."""
        super().__init__(*args, **kwargs)
        # Улучшаем отображение категорий
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = 'Выберите категорию'
    
    def clean(self):
        """Валидация формы."""
        cleaned_data = super().clean()
        budget_min = cleaned_data.get('budget_min')
        budget_max = cleaned_data.get('budget_max')
        
        # Проверка, что минимальный бюджет не больше максимального
        if budget_min and budget_max and budget_min > budget_max:
            raise forms.ValidationError({
                'budget_max': 'Максимальный бюджет должен быть больше или равен минимальному.'
            })
        
        return cleaned_data


class OfferCreateForm(forms.ModelForm):
    """
    Форма для создания предложения специалистом.
    
    Автоматически устанавливает специалиста и статус PENDING при создании.
    """
    
    class Meta:
        model = Offer
        fields = ['proposed_price', 'message']
        widgets = {
            'proposed_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Предложенная цена',
                'step': '0.01',
                'min': '0',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ваше сообщение клиенту',
                'required': True,
            }),
        }
        labels = {
            'proposed_price': 'Предложенная цена',
            'message': 'Сообщение',
        }
        help_texts = {
            'proposed_price': 'Цена, за которую вы готовы выполнить эту задачу',
            'message': 'Расскажите клиенту, почему вы подходите для этой задачи',
        }
    
    def clean_proposed_price(self):
        """Валидация предложенной цены."""
        proposed_price = self.cleaned_data.get('proposed_price')
        if proposed_price and proposed_price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля.')
        return proposed_price


class ReviewCreateForm(forms.ModelForm):
    """
    Форма для создания отзыва клиентом о специалисте.
    
    Поля: rating (1-5) и text (необязательно).
    """
    
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Оставьте комментарий о работе специалиста (необязательно)',
            }),
        }
        labels = {
            'rating': 'Оценка',
            'text': 'Комментарий (необязательно)',
        }
        help_texts = {
            'rating': 'Оцените работу специалиста от 1 до 5',
            'text': 'Дополнительные комментарии о работе специалиста',
        }
    
    def __init__(self, *args, **kwargs):
        """Инициализация формы с выбором рейтинга."""
        super().__init__(*args, **kwargs)
        # Устанавливаем choices для поля rating
        self.fields['rating'].widget.choices = [
            ('', 'Выберите оценку'),
            (1, '1 - Очень плохо'),
            (2, '2 - Плохо'),
            (3, '3 - Удовлетворительно'),
            (4, '4 - Хорошо'),
            (5, '5 - Отлично'),
        ]
    
    def clean_rating(self):
        """Валидация рейтинга."""
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError('Оценка должна быть от 1 до 5.')
        return rating


class PortfolioItemForm(forms.ModelForm):
    """
    Форма для создания/редактирования элемента портфолио.
    """
    
    class Meta:
        model = PortfolioItem
        fields = ['title', 'description', 'image', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название работы',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание работы (необязательно)',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True,
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'value': '0',
            }),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'image': 'Изображение',
            'order': 'Порядок отображения',
        }

