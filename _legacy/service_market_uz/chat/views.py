from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(
            Q(participant1=self.request.user) | Q(participant2=self.request.user)
        )
        
    def perform_create(self, serializer):
        # Logic to ensure unique conversation or get existing
        # This viewset might not need create if we handle it via a custom action or signal
        pass
        
    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a conversation with a user."""
        other_user_id = request.data.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        other_user = get_object_or_404(User, id=other_user_id)
        
        if request.user == other_user:
            return Response({'error': 'Cannot start conversation with yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if conversation exists
        conversation = Conversation.objects.filter(
            Q(participant1=request.user, participant2=other_user) |
            Q(participant1=other_user, participant2=request.user)
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create(
                participant1=request.user,
                participant2=other_user
            )
            
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a conversation."""
        conversation = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response({'error': 'content is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Update conversation timestamp
        conversation.save() # Updates updated_at
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """List messages in a conversation."""
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Mark as read
        unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
        unread_messages.update(is_read=True)
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
