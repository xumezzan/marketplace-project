from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.pricing.services import PricingEngine
from apps.wallet.services import WalletService, IdempotencyError, InsufficientFunds
from apps.wallet.models import Transaction, Wallet
from .models import Response
import uuid

class ResponseService:
    @staticmethod
    def calculate_response_price(request_obj, specialist_user):
        """
        Calculates the cost to respond.
        """
        # Determine current responses count
        current_count = request_obj.responses.count()
        
        # Determine specialist level
        level = 'NEW'
        if hasattr(specialist_user, 'specialist_profile'):
            level = specialist_user.specialist_profile.level

        # Get tariff type from category default (or specific rule if we had deeper logic)
        tariff_type = request_obj.category.default_tariff

        price = PricingEngine.calculate_price(
            category_id=request_obj.category_id,
            district_id=request_obj.district_id,
            tariff_type=tariff_type,
            budget=request_obj.budget,
            responses_count=current_count,
            specialist_level=level
        )
        
        return price, tariff_type

    @staticmethod
    def create_response(request_obj, specialist_user, message: str, idempotency_key=None):
        """
        Full orchestration: Calc Price -> Charge Wallet -> Create DB Record.
        """
        price, tariff_type = ResponseService.calculate_response_price(request_obj, specialist_user)
        
        # If tariff is COMMISSION, price to pay NOW is 0. 
        # But we record the 'potential' commission or just 0? 
        # The prompt says: "Commission is fixed sum... Paid ONLY after confirmed".
        # So for initial response, charge is 0 if commission.
        
        amount_to_charge = price if tariff_type == 'RESPONSE' else Decimal('0')

        if not idempotency_key:
            idempotency_key = uuid.uuid4()

        with transaction.atomic():
            # 1. Charge Wallet if needed
            if amount_to_charge > 0:
                WalletService.process_transaction(
                    user_id=specialist_user.id,
                    amount=-amount_to_charge, # Debit
                    transaction_type=Transaction.Type.CHARGE_RESPONSE,
                    description=f"Response to Request #{request_obj.id}",
                    idempotency_key=idempotency_key,
                    metadata={'request_id': request_obj.id}
                )

            # 2. Create Response
            # We use get_or_create to handle double-clicks not caught by idempotency key on wallet
            response, created = Response.objects.get_or_create(
                request=request_obj,
                specialist=specialist_user,
                defaults={
                    'tariff_type': tariff_type,
                    'price_paid': amount_to_charge, # What was paid NOW
                    'message': message
                }
            )
            
            if not created:
                # If already existed, check if it's the same attempt. 
                # For MVP, just return existing.
                pass

            return response
