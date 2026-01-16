from django.db import transaction
from django.utils.translation import gettext_lazy as _
from .models import Wallet, Transaction
from decimal import Decimal

class EscrowService:
    @staticmethod
    @transaction.atomic
    def lock_funds(user, amount, order):
        """
        Lock funds for a safe deal.
        """
        wallet = Wallet.objects.select_for_update().get(user=user)
        amount = Decimal(amount)
        
        if wallet.balance < amount:
            raise ValueError(_("Insufficient funds"))
            
        # Deduct from balance
        wallet.balance -= amount
        wallet.save()
        
        # Create transaction record
        Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=Transaction.Type.ESCROW_LOCK,
            description=f"Locked for Order #{order.id}"
        )
        
        return True

    @staticmethod
    @transaction.atomic
    def release_funds(order, specialist):
        """
        Release funds to the specialist upon order completion.
        """
        # We assume the funds were already locked from the client.
        # Now we credit the specialist.
        # Note: In a real system, we might track the specific locked transaction or have a separate Escrow model.
        # Here we simplify by crediting the specialist's wallet.
        
        # Get amount from order (assuming price_proposal or similar is final)
        # For now, let's assume we pass the amount or get it from the accepted response
        accepted_response = order.responses.filter(is_accepted=True).first()
        if not accepted_response:
            raise ValueError(_("No accepted response found for this order"))
            
        amount = accepted_response.price_proposal
        
        # Credit specialist
        specialist_wallet, _ = Wallet.objects.get_or_create(user=specialist)
        specialist_wallet.balance += amount
        specialist_wallet.save()
        
        Transaction.objects.create(
            wallet=specialist_wallet,
            amount=amount,
            transaction_type=Transaction.Type.ESCROW_RELEASE,
            description=f"Payment for Order #{order.id}"
        )
        
        return True

    @staticmethod
    @transaction.atomic
    def refund_funds(order, client):
        """
        Refund funds to the client if order is cancelled.
        """
        accepted_response = order.responses.filter(is_accepted=True).first()
        if not accepted_response:
             # If no response was accepted, maybe funds weren't locked? 
             # Depends on when we lock. Assuming we lock on acceptance.
             return False
             
        amount = accepted_response.price_proposal
        
        client_wallet = Wallet.objects.select_for_update().get(user=client)
        client_wallet.balance += amount
        client_wallet.save()
        
        Transaction.objects.create(
            wallet=client_wallet,
            amount=amount,
            transaction_type=Transaction.Type.ESCROW_REFUND,
            description=f"Refund for Order #{order.id}"
        )
        
        return True
