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
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(settings.BASE_DIR, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import views from the backend directory
from backend.marketplace import views
from backend import test_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('test/', test_view.test_view, name='test'),  # Test URL
    path('', views.home, name='home'),
    path('notifications/', include(('backend.notifications.urls', 'notifications'), namespace='notifications')),
    path('chat/', include(('backend.chat.urls', 'chat'), namespace='chat')),
    path('accounts/', include(('backend.accounts.urls', 'accounts'), namespace='accounts')),
    path('', include(('backend.marketplace.urls', 'marketplace'), namespace='marketplace')),
    path('api/', include('backend.marketplace.api_urls')),
    path('api/payments/', include('backend.payments.api_urls')),
]

# Поддержка MEDIA файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # В режиме разработки также обслуживаем статические файлы через Django
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
