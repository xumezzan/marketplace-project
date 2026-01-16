from rest_framework import generics, permissions, views, status
from rest_framework.response import Response as DRFResponse
from django.shortcuts import get_object_or_404
from .models import Deal
from .serializers import DealSerializer
from .services import DealService

class DealListCreateView(generics.ListCreateAPIView):
    serializer_class = DealSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Deal.objects.filter(models.Q(specialist=user) | models.Q(request__client=user))
    
    def perform_create(self, serializer):
        # Allow creating deal directly? Usually done via 'Choose Specialist' action.
        pass

class ChooseSpecialistView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        # Client chooses a specialist
        # Input: specialist_id
        specialist_id = request.data.get('specialist_id')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        specialist = get_object_or_404(User, id=specialist_id, role='SPECIALIST')
        
        # Verify request belongs to client
        # ... validation ...
        
        try:
            deal = DealService.create_deal(request_id, specialist)
            return DRFResponse(DealSerializer(deal).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return DRFResponse({'error': str(e)}, status=400)

class ContactShareView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        action = request.data.get('action') # 'request' (client) or 'approve' (specialist)

        if request.user == deal.request.client and action == 'request':
            deal.client_requested_contacts = True
        elif request.user == deal.specialist and action == 'approve':
            deal.specialist_approved_contacts = True
        else:
            return DRFResponse({'error': 'Invalid action or permissions'}, status=403)
        
        deal.save()
        is_shared = DealService.try_share_contacts(deal)
        
        return DRFResponse({
            'client_requested': deal.client_requested_contacts,
            'specialist_approved': deal.specialist_approved_contacts,
            'contacts_shared': is_shared
        })
