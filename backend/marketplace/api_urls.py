"""
API URL configuration для marketplace приложения.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    CategoryViewSet, TaskViewSet, OfferViewSet,
    UserViewSet, ReviewViewSet, DealViewSet
)
from .views import analyze_task_ai

# Создаем router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'deals', DealViewSet, basename='deal')

app_name = 'marketplace_api'

urlpatterns = [
    path('', include(router.urls)),
    path('ai/analyze-task/', analyze_task_ai, name='analyze_task_ai'),
]

