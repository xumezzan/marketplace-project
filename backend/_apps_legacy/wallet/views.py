from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from .services import WalletService
from decimal import Decimal

class MyWalletView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    def get_object(self):
        # Ensure wallet exists
        wallet, _ = Wallet.objects.get_or_create(specialist=self.request.user)
        return wallet

class MyTransactionsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(wallet__specialist=self.request.user).order_by('-created_at')

class AdminTopUpView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        # Simple manual top-up for MVP
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        
        if not user_id or not amount:
            return Response({'error': 'user_id and amount required'}, status=400)

        try:
            txn = WalletService.process_transaction(
                user_id=user_id,
                amount=Decimal(amount),
                transaction_type=Transaction.Type.TOPUP,
                description="Admin manual top-up",
                idempotency_key=request.data.get('idempotency_key') # Optional from admin
            )
            return Response({'status': 'success', 'new_balance': txn.wallet.balance})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
