"""
Views для аутентификации и управления профилем пользователя.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm


def register_view(request):
    """
    View для регистрации нового пользователя.
    """
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Аккаунт {user.username} успешно создан! Теперь вы можете войти.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    View для входа пользователя.
    """
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            
            # Редирект на следующую страницу или на главную
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    View для выхода пользователя.
    """
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')


@login_required
def profile_view(request):
    """
    View для просмотра профиля пользователя.
    """
    return render(request, 'accounts/profile.html', {'user': request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View для редактирования профиля пользователя.
    """
    model = User
    form_class = UserProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        """Возвращает текущего пользователя."""
        return self.request.user
    
    def form_valid(self, form):
        """Обработка успешной валидации формы."""
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)
