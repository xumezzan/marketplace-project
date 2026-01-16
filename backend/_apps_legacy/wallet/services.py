from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Wallet, Transaction

class InsufficientFunds(ValidationError):
    pass

class IdempotencyError(ValidationError):
    pass

class WalletService:
    @staticmethod
    @transaction.atomic
    def process_transaction(
        user_id, 
        amount: Decimal, 
        transaction_type: str, 
        description: str = "", 
        idempotency_key=None,
        metadata=None,
        allow_negative=False
    ):
        """
        Core function to handle wallet changes safely.
        amount: Positive for credit, Negative for debit.
        """
        # 1. Check idempotency
        if idempotency_key and Transaction.objects.filter(idempotency_key=idempotency_key).exists():
            return Transaction.objects.get(idempotency_key=idempotency_key)

        # 2. Lock wallet
        wallet, created = Wallet.objects.select_for_update().get_or_create(specialist_id=user_id)
        
        # 3. Validation
        if not allow_negative and (wallet.balance + amount) < 0:
            raise InsufficientFunds(f"Insufficient funds. Current: {wallet.balance}, Needed: {abs(amount)}")

        # 4. Update balance
        wallet.balance += amount
        wallet.save()

        # 5. Create transaction record
        txn = Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            idempotency_key=idempotency_key,
            metadata=metadata or {}
        )
        return txn
