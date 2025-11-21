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
    Поддерживает редактирование как основной информации (User),
    так и специфичной для роли (SpecialistProfile/ClientProfile).
    """
    model = User
    form_class = UserProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        """Возвращает текущего пользователя."""
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Добавляем форму профиля в зависимости от роли
        if user.is_specialist:
            from marketplace.models import SpecialistProfile
            from .forms import SpecialistProfileUpdateForm
            # Создаем профиль, если его нет
            profile, _ = SpecialistProfile.objects.get_or_create(user=user)
            if 'specialist_form' not in context:
                context['specialist_form'] = SpecialistProfileUpdateForm(instance=profile)
                
        if user.is_client:
            from marketplace.models import ClientProfile
            from .forms import ClientProfileUpdateForm
            # Создаем профиль, если его нет
            profile, _ = ClientProfile.objects.get_or_create(user=user)
            if 'client_form' not in context:
                context['client_form'] = ClientProfileUpdateForm(instance=profile)
                
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = self.get_form()
        
        valid = user_form.is_valid()
        
        specialist_form = None
        client_form = None
        
        if self.object.is_specialist:
            from marketplace.models import SpecialistProfile
            from .forms import SpecialistProfileUpdateForm
            profile, _ = SpecialistProfile.objects.get_or_create(user=self.object)
            specialist_form = SpecialistProfileUpdateForm(request.POST, instance=profile)
            valid = valid and specialist_form.is_valid()
            
        if self.object.is_client:
            from marketplace.models import ClientProfile
            from .forms import ClientProfileUpdateForm
            profile, _ = ClientProfile.objects.get_or_create(user=self.object)
            client_form = ClientProfileUpdateForm(request.POST, instance=profile)
            valid = valid and client_form.is_valid()
            
        if valid:
            return self.form_valid(user_form, specialist_form, client_form)
        else:
            return self.form_invalid(user_form, specialist_form, client_form)
            
    def form_valid(self, user_form, specialist_form=None, client_form=None):
        """Сохраняем все валидные формы."""
        user_form.save()
        
        if specialist_form:
            specialist_form.save()
            
        if client_form:
            client_form.save()
            
        messages.success(self.request, 'Профиль успешно обновлен!')
        return redirect(self.success_url)
        
    def form_invalid(self, user_form, specialist_form=None, client_form=None):
        """Рендерим страницу с ошибками."""
        return self.render_to_response(self.get_context_data(
            form=user_form,
            specialist_form=specialist_form,
            client_form=client_form
        ))
