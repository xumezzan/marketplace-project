from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from datetime import timedelta
from .models import Response
from apps.wallet.services import WalletService
from apps.wallet.models import Transaction, Wallet
import uuid

@shared_task
def process_refunds_for_unviewed_responses():
    """
    Finds responses that are:
    1. Tariff type RESPONSE
    2. Not viewed by client
    3. Older than REFUND_TTL_HOURS
    4. Refund not yet processed
    And refunds them.
    """
    ttl_hours = getattr(settings, 'REFUND_TTL_HOURS', 24)
    threshold = timezone.now() - timedelta(hours=ttl_hours)
    
    # Batch processing could be better, but for MVP simple loop is okay
    # We use iterator to avoid memory issues if there are many
    candidates = Response.objects.filter(
        tariff_type='RESPONSE',
        viewed_at_by_client__isnull=True,
        refund_processed=False,
        created_at__lt=threshold,
        price_paid__gt=0 # Only refund if they actually paid
    ).select_related('specialist')

    refunded_count = 0
    
    for resp in candidates:
        try:
            with transaction.atomic():
                # Lock the response row to prevent race conditions (double refund)
                locked_resp = Response.objects.select_for_update().get(id=resp.id)
                
                if locked_resp.refund_processed:
                    continue
                
                # Refund to Wallet
                WalletService.process_transaction(
                    user_id=locked_resp.specialist.id,
                    amount=locked_resp.price_paid, # Credit back
                    transaction_type=Transaction.Type.REFUND_RESPONSE,
                    description=f"Refund for unviewed response #{locked_resp.id}",
                    idempotency_key=uuid.uuid4(), # Unique for this refund action
                    metadata={'response_id': locked_resp.id}
                )

                # Mark processed
                locked_resp.refund_processed = True
                locked_resp.save(update_fields=['refund_processed'])
                
                refunded_count += 1
        except Exception as e:
            # Log error but continue processing others
            print(f"Error refunding response {resp.id}: {e}")

    return f"Refunded {refunded_count} responses"
