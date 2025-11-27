from rest_framework import serializers
from .models import Wallet, Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'description', 'created_at']

class WalletSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['balance', 'transactions']
