from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, PortfolioItemViewSet, UserViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')
router.register(r'portfolio', PortfolioItemViewSet, basename='portfolio')

urlpatterns = [
    path('', include(router.urls)),
]
