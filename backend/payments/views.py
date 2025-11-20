from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Wallet
from .serializers import WalletSerializer

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для кошелька.
    
    Позволяет пользователю просматривать свой баланс и историю транзакций.
    Также содержит методы для пополнения и вывода (mock).
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает только кошелек текущего пользователя."""
        return Wallet.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Возвращает кошелек текущего пользователя (создает если нет)."""
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet
    
    @action(detail=False, methods=['post'])
    def deposit(self, request):
        """
        Пополнение кошелька (Mock).
        
        Принимает:
        - amount: сумма пополнения
        """
        amount = request.data.get('amount')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {'error': 'Некорректная сумма.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        wallet = self.get_object()
        wallet.deposit(amount)
        
        return Response({'status': 'success', 'balance': wallet.balance})
        
    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """
        Вывод средств (Mock).
        
        Принимает:
        - amount: сумма вывода
        """
        amount = request.data.get('amount')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {'error': 'Некорректная сумма.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        wallet = self.get_object()
        try:
            wallet.withdraw(amount)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'status': 'success', 'balance': wallet.balance})
