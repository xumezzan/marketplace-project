from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.db import transaction
from .models import Deal
from .payment_models import FirstPaymentConfirmation
from apps.pricing.services import PricingEngine
from apps.wallet.services import WalletService, Transaction
import uuid

class CommissionService:
    @staticmethod
    def generate_code(deal: Deal, user):
        """
        Specialist generates a code to show to the client.
        """
        # Security: Only specialist can generate
        if deal.specialist != user:
            raise PermissionError("Only specialist can generate code")
        
        # Check if already confirmed
        if hasattr(deal, 'payment_confirmation') and deal.payment_confirmation.confirmed_at:
             raise ValueError("Already confirmed")

        # Generate 6 digit code
        raw_code = get_random_string(length=6, allowed_chars='0123456789')
        code_hash = make_password(raw_code)
        
        confirmation, created = FirstPaymentConfirmation.objects.update_or_create(
            deal=deal,
            defaults={'code_hash': code_hash, 'generated_at': timezone.now()}
        )
        return raw_code

    @staticmethod
    def confirm_payment(deal: Deal, client_user, code: str):
        """
        Client inputs code. Atomic charge commission.
        """
        if deal.request.client != client_user:
             raise PermissionError("Only client can confirm payment")
        
        conf = getattr(deal, 'payment_confirmation', None)
        if not conf:
            raise ValueError("No confirmation code generated")
        
        if conf.confirmed_at:
             return True # Idempotent-ish

        if not check_password(code, conf.code_hash):
             raise ValueError("Invalid code")

        # Calculate Commission
        # We need to know 'commission amount'. 
        # Re-calculate or use stored? Re-calculate based on current rules? 
        # Ideally should have been snapshot at Deal creation. 
        # For MVP, calculate now using PricingEngine.
        
        from apps.responses.services import ResponseService
        # Reuse logic? ResponseService uses PricingEngine.
        # But we need tariff_type=COMMISSION logic.
        
        req = deal.request
        responses_count = req.responses.count()
        level = deal.specialist.specialist_profile.level
        
        price = PricingEngine.calculate_price(
            category_id=req.category_id,
            district_id=req.district_id,
            tariff_type='COMMISSION',
            budget=req.budget,
            responses_count=responses_count,
            specialist_level=level
        )
        
        with transaction.atomic():
            # 1. Charge Wallet
            WalletService.process_transaction(
                user_id=deal.specialist.id,
                amount=-price,
                transaction_type=Transaction.Type.CHARGE_COMMISSION,
                description=f"Commission for Deal #{deal.id}",
                idempotency_key=uuid.uuid4(),
                metadata={'deal_id': deal.id},
                allow_negative=True # Can go negative for commission? Maybe yes, debt.
            )
            
            # 2. Mark confirmed
            conf.confirmed_at = timezone.now()
            conf.confirmed_by = client_user
            conf.save()
            
            # 3. Mark Deal Completed?
            deal.status = Deal.Status.COMPLETED
            deal.save()
            
        return True
