"""
URL configuration for marketplace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language

from django.shortcuts import render
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(settings.BASE_DIR, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, settings.BASE_DIR)

from marketplace import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('', views.home, name='home'),
    path('test/', lambda request: render(request, 'test.html', {'count': 42})),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    path('notifications/', include('notifications.urls')),
    path('', include('marketplace.urls')),
    path('api/', include('marketplace.api_urls')),
    path('api/payments/', include('payments.api_urls')),
]

# Поддержка MEDIA файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # В режиме разработки также обслуживаем статические файлы через Django
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
