from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from apps.deals.models import Deal

class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(models.Q(deal__specialist=user) | models.Q(deal__request__client=user))
    
    def perform_create(self, serializer):
        # Create chat for deal
        deal_id = self.request.data.get('deal')
        deal = get_object_or_404(Deal, pk=deal_id)
        # Check permissions
        if self.request.user not in [deal.specialist, deal.request.client]:
             raise permissions.PermissionDenied("Not part of this deal")
        serializer.save(deal=deal)

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, pk=chat_id)
        if self.request.user not in [chat.deal.specialist, chat.deal.request.client]:
             return Message.objects.none()
        return Message.objects.filter(chat=chat)

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, pk=chat_id)
        if self.request.user not in [chat.deal.specialist, chat.deal.request.client]:
             raise permissions.PermissionDenied("Not part of this chat")
        serializer.save(chat=chat, sender=self.request.user)
