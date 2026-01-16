from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from .models import Deal
from .commission_services import CommissionService

class GenerateCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        try:
            code = CommissionService.generate_code(deal, request.user)
            return Response({'code': code})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class ConfirmPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code required'}, status=400)
            
        try:
            CommissionService.confirm_payment(deal, request.user, code)
            return Response({'status': 'confirmed'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
