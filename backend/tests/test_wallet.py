import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.wallet.services import WalletService, InsufficientFunds
from apps.wallet.models import Wallet, Transaction
import uuid
from django.db import transaction

User = get_user_model()

@pytest.fixture
def specialist():
    return User.objects.create_user(email='spec@test.com', phone='998901234567', role='SPECIALIST')

@pytest.mark.django_db
class TestWalletService:
    def test_topup(self, specialist):
        txn = WalletService.process_transaction(
            user_id=specialist.id,
            amount=Decimal('100000'),
            transaction_type=Transaction.Type.TOPUP
        )
        wallet = Wallet.objects.get(specialist=specialist)
        assert wallet.balance == 100000
        assert txn.amount == 100000

    def test_insufficient_funds(self, specialist):
        # Initial 0 balance
        with pytest.raises(InsufficientFunds):
            WalletService.process_transaction(
                user_id=specialist.id,
                amount=Decimal('-1000'),
                transaction_type=Transaction.Type.CHARGE_RESPONSE
            )

    def test_idempotency(self, specialist):
        key = uuid.uuid4()
        # First call
        txn1 = WalletService.process_transaction(
            user_id=specialist.id,
            amount=Decimal('10000'),
            transaction_type=Transaction.Type.TOPUP,
            idempotency_key=key
        )
        # Second call with same key
        txn2 = WalletService.process_transaction(
            user_id=specialist.id,
            amount=Decimal('10000'),
            transaction_type=Transaction.Type.TOPUP,
            idempotency_key=key
        )
        
        wallet = Wallet.objects.get(specialist=specialist)
        assert wallet.balance == 10000 # Should only apply once
        assert txn1.id == txn2.id

    def test_atomic_transaction_rollback(self, specialist):
        # Ensure if error happens, balance is not touched
        initial_balance = Decimal('50000')
        WalletService.process_transaction(specialist.id, initial_balance, Transaction.Type.TOPUP)
        
        try:
            with transaction.atomic():
                WalletService.process_transaction(specialist.id, Decimal('-10000'), Transaction.Type.CHARGE_RESPONSE)
                raise Exception("Something went wrong")
        except Exception:
            pass
        
        wallet = Wallet.objects.get(specialist=specialist)
        assert wallet.balance == initial_balance # Should be rolled back to 50000
