from django.urls import path
from .views import CategoryListView, DistrictListView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('districts/', DistrictListView.as_view(), name='district-list'),
]
