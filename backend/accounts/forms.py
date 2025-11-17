"""
Формы для аутентификации и регистрации пользователей.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.
    
    Поля: username, email, password1, password2, role, phone, city.
    """
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com',
        })
    )
    role = forms.ChoiceField(
        label='Роль',
        choices=User.Role.choices,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text='Выберите, будете ли вы клиентом или специалистом'
    )
    phone = forms.CharField(
        label='Телефон',
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+998901234567',
        })
    )
    city = forms.CharField(
        label='Город',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ташкент',
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'phone', 'city')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'username',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Улучшаем стили полей паролей
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Минимум 8 символов',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
        })
    
    def clean_email(self):
        """Проверка уникальности email."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email


class UserLoginForm(AuthenticationForm):
    """
    Форма входа пользователя.
    """
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
        })
    )
    
    error_messages = {
        'invalid_login': 'Неверное имя пользователя или пароль.',
        'inactive': 'Этот аккаунт неактивен.',
    }


class UserProfileUpdateForm(forms.ModelForm):
    """
    Форма для обновления профиля пользователя.
    """
    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name', 'email', 'phone', 'city')
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'avatar': 'Аватар',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'phone': 'Телефон',
            'city': 'Город',
        }

