from rest_framework import serializers
from .models import Wallet, Transaction

class TransactionSerializer(serializers.ModelSerializer):
    """Сериализатор для транзакций."""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'type', 'type_display', 'description', 'created_at']
        read_only_fields = ['id', 'amount', 'type', 'description', 'created_at']

class WalletSerializer(serializers.ModelSerializer):
    """Сериализатор для кошелька."""
    
    transactions = TransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'transactions']
        read_only_fields = ['id', 'balance', 'transactions']
