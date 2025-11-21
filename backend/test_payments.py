import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from backend.marketplace.models import Task, Offer, Deal, Escrow, Category
from payments.models import Wallet
from payments.services import PaymentService

User = get_user_model()

def test_payments():
    print("--- Testing Payment System ---")
    
    # 1. Setup Users
    client_username = 'test_client_pay'
    specialist_username = 'test_spec_pay'
    
    try:
        client = User.objects.get(username=client_username)
    except User.DoesNotExist:
        client = User.objects.create_user(username=client_username, email='c@ex.com', password='p')
        client.is_client = True
        client.save()
        
    try:
        specialist = User.objects.get(username=specialist_username)
    except User.DoesNotExist:
        specialist = User.objects.create_user(username=specialist_username, email='s@ex.com', password='p')
        specialist.is_specialist = True
        specialist.save()
        
    # Ensure wallets exist (signals should handle this, but let's be safe)
    Wallet.objects.get_or_create(user=client)
    Wallet.objects.get_or_create(user=specialist)
    
    # 2. Deposit Funds
    initial_deposit = Decimal('5000.00')
    client.wallet.deposit(initial_deposit)
    print(f"Client balance: {client.wallet.balance}")
    
    # 3. Create Deal Flow
    category, _ = Category.objects.get_or_create(name='Test Cat', slug='test-cat')
    task = Task.objects.create(
        client=client,
        category=category,
        title='Test Task',
        description='Desc',
        budget_min=100,
        budget_max=200,
        city='Moscow'
    )
    
    offer = Offer.objects.create(
        task=task,
        specialist=specialist,
        proposed_price=Decimal('1000.00'),
        message='I can do it'
    )
    
    # Accept offer -> Create Deal
    offer.accept() # This creates deal via signal? No, logic is in viewset usually.
    # Let's manually create deal as viewset does
    deal = Deal.objects.create(
        task=task,
        offer=offer,
        client=client,
        specialist=specialist,
        final_price=offer.proposed_price,
        status=Deal.Status.PENDING
    )
    print(f"Deal created: {deal.status}")
    
    # 4. Process Payment (Lock funds)
    print("Processing payment...")
    success = PaymentService.process_payment(deal)
    print(f"Payment success: {success}")
    
    client.wallet.refresh_from_db()
    deal.refresh_from_db()
    print(f"Client balance after lock: {client.wallet.balance}")
    print(f"Deal status: {deal.status}")
    
    try:
        escrow = deal.escrow
        print(f"Escrow created: {escrow.amount} ({escrow.status})")
    except Escrow.DoesNotExist:
        print("Escrow NOT created!")
        
    # 5. Release Payment
    print("Releasing payment...")
    success = PaymentService.release_payment(deal)
    print(f"Release success: {success}")
    
    specialist.wallet.refresh_from_db()
    deal.refresh_from_db()
    escrow.refresh_from_db()
    
    print(f"Specialist balance: {specialist.wallet.balance}")
    print(f"Deal status: {deal.status}")
    print(f"Escrow status: {escrow.status}")
    
    # Verify math
    expected_payout = Decimal('1000.00') * Decimal('0.90') # 900
    if specialist.wallet.balance >= expected_payout:
        print("Math seems correct.")
    else:
        print(f"Math ERROR: Expected >= {expected_payout}, got {specialist.wallet.balance}")

    print("--- Test Finished ---")

if __name__ == '__main__':
    test_payments()
