from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for users to view their wallet balance and history.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Return the single wallet object for the user
        wallet = self.get_queryset().first()
        if not wallet:
            return Response({"detail": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='top-up')
    def top_up(self, request):
        """
        Dev-only endpoint to add funds.
        """
        amount = request.data.get('amount')
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        wallet = self.get_queryset().first()
        if not wallet:
             # Should be created by signal, but just in case
             wallet = Wallet.objects.create(user=request.user)

        with transaction.atomic():
            wallet.balance += amount
            wallet.save()
            
            Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=Transaction.Type.DEPOSIT,
                description="Manual Top-up"
            )
            
        return Response({"message": f"Successfully added {amount} to wallet.", "new_balance": wallet.balance})
