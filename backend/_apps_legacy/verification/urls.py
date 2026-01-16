from django.urls import path
from .views import DocumentListCreateView

urlpatterns = [
    path('documents/', DocumentListCreateView.as_view(), name='verification-documents'),
]
