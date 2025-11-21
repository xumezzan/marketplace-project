import json
import base64
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Wallet, Transaction
from .serializers import WalletSerializer
from .payme_service import PaymeService

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра кошелька и истории транзакций.
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def get_object(self):
        # Всегда возвращаем кошелек текущего пользователя
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        """
        Mock-метод для пополнения (для тестов).
        В реале пополнение идет через Payme/Stripe.
        """
        wallet = self.get_object()
        amount = request.data.get('amount')
        
        try:
            amount = Decimal(amount)
            wallet.deposit(amount)
            return Response({'status': 'ok', 'balance': wallet.balance})
        except (ValueError, TypeError, Decimal.InvalidOperation) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """
        Mock-метод для вывода.
        """
        wallet = self.get_object()
        amount = request.data.get('amount')
        
        try:
            amount = Decimal(amount)
            wallet.withdraw(amount)
            return Response({'status': 'ok', 'balance': wallet.balance})
        except (ValueError, TypeError, Decimal.InvalidOperation) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class PaymeView(View):
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        # 1. Basic Auth Check
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("Payme webhook called without Authorization header")
            return JsonResponse({'error': {'code': -32504, 'message': 'Недостаточно привилегий'}})
        
        # "Basic base64(login:password)"
        try:
            auth_parts = auth_header.split(' ')
            if len(auth_parts) != 2 or auth_parts[0] != 'Basic':
                logger.warning(f"Invalid Authorization header format: {auth_header[:20]}...")
                return JsonResponse({'error': {'code': -32504, 'message': 'Неверный формат авторизации'}})
            
            encoded_credentials = auth_parts[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            login, password = decoded_credentials.split(':', 1)
            
            # Verify credentials from settings
            if login != settings.PAYME_LOGIN or password != settings.PAYME_KEY:
                logger.warning(f"Invalid Payme credentials from login: {login}")
                return JsonResponse({'error': {'code': -32504, 'message': 'Неверные учетные данные'}})
                
        except (ValueError, UnicodeDecodeError, IndexError) as e:
            logger.error(f"Error decoding Payme auth header: {e}", exc_info=True)
            return JsonResponse({'error': {'code': -32504, 'message': 'Ошибка авторизации'}})

        # 2. Parse JSON-RPC
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': {'code': -32700, 'message': 'Ошибка парсинга JSON'}})

        method = data.get('method')
        params = data.get('params')
        
        service = PaymeService()
        response_data = {}

        if method == 'CheckPerformTransaction':
            response_data = service.check_perform_transaction(params)
        elif method == 'CreateTransaction':
            response_data = service.create_transaction(params)
        elif method == 'PerformTransaction':
            response_data = service.perform_transaction(params)
        elif method == 'CancelTransaction':
            response_data = service.cancel_transaction(params)
        elif method == 'CheckTransaction':
            response_data = service.check_transaction(params)
        else:
            response_data = {'error': {'code': -32601, 'message': 'Метод не найден'}}

        # Добавляем id запроса в ответ (по стандарту JSON-RPC)
        response_data['id'] = data.get('id')
        response_data['jsonrpc'] = '2.0'
        
        return JsonResponse(response_data)
