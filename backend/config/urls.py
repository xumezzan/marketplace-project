from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/catalog/', include('apps.catalog.urls')),
    path('api/requests/', include('apps.requests.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
    path('api/verification/', include('apps.verification.urls')),
    path('api/responses/', include('apps.responses.urls')),
    path('api/deals/', include('apps.deals.urls')),
    path('api/chats/', include('apps.chat.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
]
