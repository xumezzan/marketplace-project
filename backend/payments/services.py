from decimal import Decimal
from django.db import transaction
from django.conf import settings
from marketplace.models import Deal
from .models import Wallet, Transaction

class PaymentService:
    @staticmethod
    @transaction.atomic
    def release_funds(deal: Deal):
        """
        Release funds to the specialist after task completion.
        Calculates commission and transfers the rest to the specialist's wallet.
        """
        # 1. Validation
        if deal.status != Deal.Status.IN_PROGRESS:
            raise ValueError("Deal must be IN_PROGRESS (Paid) to release funds")
            
        # 2. Calculate Commission
        commission_rate = getattr(settings, 'PLATFORM_COMMISSION_RATE', Decimal('0.10'))
        total_amount = Decimal(deal.final_price)
        commission_amount = total_amount * commission_rate
        payout_amount = total_amount - commission_amount
        
        # 3. Update Deal
        deal.commission_amount = commission_amount
        deal.status = Deal.Status.COMPLETED
        deal.save()
        
        # 4. Transfer to Specialist Wallet
        specialist_wallet, _ = Wallet.objects.get_or_create(user=deal.specialist)
        specialist_wallet.deposit(payout_amount)
        
        # 5. Record Platform Fee (Optional: could be a transaction on a system wallet)
        # For now, we just record it in the deal.
        
        return {
            'success': True,
            'payout_amount': payout_amount,
            'commission_amount': commission_amount
        }
