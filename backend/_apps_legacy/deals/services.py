from django.utils import timezone
from .models import Deal
from apps.requests.models import Request

class DealService:
    @staticmethod
    def create_deal(request_id, specialist_user):
        req = Request.objects.get(id=request_id)
        # Check if already has deal
        if hasattr(req, 'deal'):
             raise ValueError("Request already has a deal")
        
        deal = Deal.objects.create(
            request=req,
            specialist=specialist_user
        )
        # Close request? Or keep it open until completion? 
        # Usually deal creation closes the search.
        req.status = Request.Status.CLOSED
        req.save()
        return deal

    @staticmethod
    def try_share_contacts(deal: Deal):
        """
        Checks if both flags are true, and if so, sets shared_at timestamp.
        """
        if deal.client_requested_contacts and deal.specialist_approved_contacts and not deal.contacts_shared_at:
            deal.contacts_shared_at = timezone.now()
            deal.save()
            return True
        return False
