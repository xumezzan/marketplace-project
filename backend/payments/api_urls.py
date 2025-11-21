from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, PaymeView

router = DefaultRouter()
router.register(r'wallet', WalletViewSet, basename='wallet')

app_name = 'payments_api'

urlpatterns = [
    path('', include(router.urls)),
    path('payme/', PaymeView.as_view(), name='payme'),
]
