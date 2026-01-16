from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderResponse
from .serializers import OrderSerializer, OrderResponseSerializer

class IsClientOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'client'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.client == request.user


from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['description', 'address']
    ordering_fields = ['created_at', 'deadline']

    def get_queryset(self):
        queryset = Order.objects.filter(status=Order.Status.PUBLISHED)
        user = self.request.user
        
        # Filter by distance
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        radius = self.request.query_params.get('radius') # in meters
        
        if lat and lon and radius:
            try:
                user_location = Point(float(lon), float(lat), srid=4326)
                queryset = queryset.annotate(
                    distance=Distance('location', user_location)
                ).filter(distance__lte=radius).order_by('distance')
            except (ValueError, TypeError):
                pass # Ignore invalid params

        if user.is_authenticated and user.role == 'client':
            # Clients see their own orders + all published
            return queryset | Order.objects.filter(client=user)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        """List responses for a specific order (Only for owner)."""
        order = self.get_object()
        if order.client != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        
        responses = order.responses.all()
        serializer = OrderResponseSerializer(responses, many=True)
        return Response(serializer.data)


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = OrderResponse.objects.all()
    serializer_class = OrderResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'specialist':
            return OrderResponse.objects.filter(specialist=user)
        elif user.role == 'client':
            # Clients see responses to THEIR orders
            return OrderResponse.objects.filter(order__client=user)
        return OrderResponse.objects.none()

    def perform_create(self, serializer):
        from django.conf import settings
        from django.db import transaction
        from rest_framework.exceptions import ValidationError
        from wallet.models import Wallet, Transaction
        
        user = self.request.user
        cost = getattr(settings, 'RESPONSE_COST', 5000)
        
        with transaction.atomic():
            # Lock the wallet row for update
            try:
                wallet = Wallet.objects.select_for_update().get(user=user)
            except Wallet.DoesNotExist:
                raise ValidationError("Wallet not found.")
                
            if wallet.balance < cost:
                raise ValidationError(f"Insufficient funds. You need {cost} UZS to respond to this order.")
            
            # Check Verification
            if not hasattr(user, 'specialist_profile') or not user.specialist_profile.is_verified:
                raise ValidationError("Only verified specialists can respond to orders.")

            # Deduct funds
            wallet.balance -= cost
            wallet.save()
            
            # Create Transaction Record
            Transaction.objects.create(
                wallet=wallet,
                amount=cost,
                transaction_type=Transaction.Type.WITHDRAWAL,
                description=f"Payment for response to Order #{serializer.validated_data['order'].id}"
            )
            
            # Save Response
            serializer.save(specialist=user)
