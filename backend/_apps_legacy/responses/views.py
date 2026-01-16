from rest_framework import generics, permissions, status
from rest_framework.response import Response as DRFResponse
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.requests.models import Request
from .models import Response
from .serializers import ResponseSerializer, CreateResponseSerializer
from .services import ResponseService
from django.utils import timezone

class RequestResponseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """Pre-check price"""
        req_obj = get_object_or_404(Request, pk=pk)
        price, tariff = ResponseService.calculate_response_price(req_obj, request.user)
        return DRFResponse({
            'tariff_type': tariff,
            'price': price,
            'currency': 'UZS'
        })

    def post(self, request, pk):
        """Commit response"""
        req_obj = get_object_or_404(Request, pk=pk)
        serializer = CreateResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            resp = ResponseService.create_response(
                request_obj=req_obj,
                specialist_user=request.user,
                message=serializer.validated_data.get('message', ''),
                idempotency_key=request.headers.get('Idempotency-Key')
            )
            return DRFResponse(ResponseSerializer(resp).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return DRFResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MyResponsesView(generics.ListAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Response.objects.filter(specialist=self.request.user)

class MarkResponseViewedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        resp = get_object_or_404(Response, pk=pk)
        # Verify it's the client of the request
        if resp.request.client != request.user:
            return DRFResponse({'error': 'Not authorized'}, status=403)
        
        if not resp.viewed_at_by_client:
            resp.viewed_at_by_client = timezone.now()
            resp.save()
        
        return DRFResponse({'status': 'viewed'})
