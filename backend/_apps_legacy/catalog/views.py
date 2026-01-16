from rest_framework import generics, permissions
from .models import Category, District
from .serializers import CategorySerializer, DistrictSerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True, is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class DistrictListView(generics.ListAPIView):
    queryset = District.objects.all().order_by('name')
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]
