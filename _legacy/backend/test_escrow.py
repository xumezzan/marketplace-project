import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from marketplace.models import Deal, Task, Category, Offer
from payments.services import PaymentService
from payments.models import Wallet

User = get_user_model()

def test_escrow_flow():
    print("Testing Escrow Flow...")
    
    # 1. Setup Data
    client, _ = User.objects.get_or_create(username='client_test', defaults={'email': 'client@test.com'})
    specialist, _ = User.objects.get_or_create(username='spec_test', defaults={'email': 'spec@test.com'})
    category, _ = Category.objects.get_or_create(name='Test Category')
    
    task = Task.objects.create(
        client=client,
        category=category,
        title='Test Task',
        description='Test Description',
        status=Task.Status.PUBLISHED
    )
    
    offer = Offer.objects.create(
        task=task,
        specialist=specialist,
        proposed_price=100000,
        status=Offer.Status.ACCEPTED
    )
    
    deal = Deal.objects.create(
        task=task,
        offer=offer,
        client=client,
        specialist=specialist,
        final_price=100000,
        status=Deal.Status.IN_PROGRESS # Simulate Paid
    )
    
    print(f"Deal created: {deal.id}, Status: {deal.status}, Price: {deal.final_price}")
    
    # 2. Release Funds
    print("Releasing funds...")
    result = PaymentService.release_funds(deal)
    
    # 3. Verify
    deal.refresh_from_db()
    specialist_wallet = Wallet.objects.get(user=specialist)
    
    print(f"Deal Status: {deal.status}")
    print(f"Commission: {deal.commission_amount}")
    print(f"Specialist Wallet Balance: {specialist_wallet.balance}")
    
    assert deal.status == Deal.Status.COMPLETED
    assert deal.commission_amount == Decimal('10000.00') # 10% of 100,000
    assert specialist_wallet.balance >= Decimal('90000.00')
    
    print("SUCCESS: Escrow flow verified!")
    
    # 4. Test Withdrawal
    print("Testing Withdrawal...")
    initial_balance = specialist_wallet.balance
    withdraw_amount = Decimal('50000.00')
    specialist_wallet.withdraw(withdraw_amount)
    
    specialist_wallet.refresh_from_db()
    print(f"Wallet Balance after withdrawal: {specialist_wallet.balance}")
    
    assert specialist_wallet.balance == initial_balance - withdraw_amount
    print("SUCCESS: Withdrawal verified!")

if __name__ == '__main__':
    try:
        test_escrow_flow()
    except Exception as e:
        print(f"FAILED: {e}")
