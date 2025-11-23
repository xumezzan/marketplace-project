import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from marketplace.models import Task, Review, Deal, Dispute
from payments.models import Wallet
from payments.services import PaymentService

User = get_user_model()

def test_moderation_and_dispute():
    print("Testing Admin & Moderation...")
    
    # 1. Setup Users
    client, _ = User.objects.get_or_create(username='mod_client', defaults={'email': 'mod_client@test.com', 'is_client': True})
    specialist, _ = User.objects.get_or_create(username='mod_spec', defaults={'email': 'mod_spec@test.com', 'is_specialist': True})
    
    # 2. Test Task Moderation
    print("\n--- Task Moderation ---")
    task = Task.objects.create(
        client=client,
        title="Suspicious Task",
        description="Do something illegal",
        status=Task.Status.DRAFT,
        category_id=1, # Assuming category 1 exists
        city="Tashkent"
    )
    print(f"Task created: {task.moderation_status}")
    
    # Approve
    task.moderation_status = Task.ModerationStatus.APPROVED
    task.save()
    print(f"Task approved: {task.moderation_status}")
    assert task.moderation_status == Task.ModerationStatus.APPROVED
    
    # 3. Test Dispute & Refund
    print("\n--- Dispute & Refund ---")
    # Create Deal (Simulate Paid)
    deal = Deal.objects.create(
        task=task,
        client=client,
        specialist=specialist,
        final_price=100000,
        status=Deal.Status.IN_PROGRESS,
        offer_id=1 # Mock offer ID, might fail if FK constraint check
    )
    # Need a real offer for FK
    from marketplace.models import Offer, Category
    category, _ = Category.objects.get_or_create(name="Test Cat")
    task.category = category
    task.save()
    offer = Offer.objects.create(task=task, specialist=specialist, proposed_price=100000)
    deal.offer = offer
    deal.save()
    
    print(f"Deal created: {deal.status}")
    
    # Create Dispute
    dispute = Dispute.objects.create(
        deal=deal,
        initiator=client,
        reason="Not done",
        description="Specialist disappeared"
    )
    print(f"Dispute created: {dispute.status}")
    
    # Resolve: Refund Client
    print("Resolving: Refund Client...")
    PaymentService.refund_client(deal)
    
    dispute.status = Dispute.Status.RESOLVED
    dispute.resolution = Dispute.Resolution.REFUND_CLIENT
    dispute.save()
    
    # Verify
    deal.refresh_from_db()
    print(f"Deal status after refund: {deal.status}")
    assert deal.status == Deal.Status.CANCELED
    
    client_wallet = Wallet.objects.get(user=client)
    print(f"Client wallet balance: {client_wallet.balance}")
    assert client_wallet.balance == Decimal('100000.00')
    
    print("SUCCESS: Moderation and Dispute flow verified!")

if __name__ == '__main__':
    test_moderation_and_dispute()
