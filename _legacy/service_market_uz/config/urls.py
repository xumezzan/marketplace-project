from django.contrib import admin
from django.urls import path, include
from core.views import index

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('api/v1/services/', include('services.urls')),
    path('api/v1/orders/', include('orders.urls')),
    path('api/v1/reviews/', include('reviews.urls')),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/wallet/', include('wallet.urls')),
    path('api/v1/chat/', include('chat.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
]
