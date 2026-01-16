from django.urls import path
from .views import RequestListCreateView, RequestDetailView

urlpatterns = [
    path('', RequestListCreateView.as_view(), name='request-list'),
    path('<int:pk>/', RequestDetailView.as_view(), name='request-detail'),
]
