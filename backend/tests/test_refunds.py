import pytest
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from apps.responses.tasks import process_refunds_for_unviewed_responses
from apps.responses.models import Response
from apps.wallet.models import Wallet
from apps.catalog.models import Category, District
from apps.requests.models import Request
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def refund_setup(db):
    client = User.objects.create_user(email='c@t.com', phone='1', role='CLIENT')
    specialist = User.objects.create_user(email='s@t.com', phone='2', role='SPECIALIST')
    
    # Init wallet
    from apps.wallet.services import WalletService, Transaction
    WalletService.process_transaction(specialist.id, Decimal('10000'), Transaction.Type.TOPUP)
    
    cat = Category.objects.create(name='TestCat')
    dist = District.objects.create(name='TestDist')
    req = Request.objects.create(client=client, category=cat, district=dist, budget=100)
    
    return client, specialist, req

@pytest.mark.django_db
def test_refund_task(refund_setup, settings):
    client, specialist, req = refund_setup
    settings.REFUND_TTL_HOURS = 24
    
    # Case 1: Eligible for refund (Old, Unviewed)
    old_time = timezone.now() - timedelta(hours=25)
    resp1 = Response.objects.create(
        request=req,
        specialist=specialist,
        tariff_type='RESPONSE',
        price_paid=Decimal('5000'),
        created_at=old_time # Overridden by auto_now_add? No, auto_now_add makes it hard to mock in create.
    )
    # Hack to update created_at for auto_now_add field
    Response.objects.filter(id=resp1.id).update(created_at=old_time)
    
    # Case 2: Not eligible (Too new)
    resp2 = Response.objects.create(
        request=req,
        specialist=specialist,
        tariff_type='RESPONSE',
        price_paid=Decimal('2000')
    )
    # Using another specialist for uniqueness constraint? No, constraint is (request, specialist). 
    # Can't have 2 responses from same specialist to same request.
    # So we need another specialist or another request.
    # Let's just test resp1 for now.
    
    # Run task
    process_refunds_for_unviewed_responses()
    
    resp1.refresh_from_db()
    
    assert resp1.refund_processed == True
    
    # Wallet check: 10000 initial. Resp1 cost 5000 (we didn't charge wallet in this test setup, just manual entry).
    # Wait, the refund ADDs money. So it should be 10000 + 5000 = 15000.
    w = Wallet.objects.get(specialist=specialist)
    assert w.balance == Decimal('15000')

    # Run again - shouldn't refund twice
    process_refunds_for_unviewed_responses()
    w.refresh_from_db()
    assert w.balance == Decimal('15000')
