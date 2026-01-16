from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Request
from .serializers import RequestSerializer

class IsClientOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'CLIENT'

class RequestListCreateView(generics.ListCreateAPIView):
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'district', 'status']
    search_fields = ['description']
    ordering_fields = ['created_at', 'budget']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return Request.objects.filter(client=user)
        elif user.role == 'SPECIALIST':
            # Specialists see open requests in their categories/districts (simplified for MVP: see all OPEN)
            return Request.objects.filter(status='OPEN')
        elif user.role == 'ADMIN':
            return Request.objects.all()
        return Request.objects.none()

class RequestDetailView(generics.RetrieveUpdateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        # Only allow closing
        if 'status' in serializer.validated_data and serializer.validated_data['status'] == 'CLOSED':
            serializer.save()
        # Full update logic to be refined
