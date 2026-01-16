"""
WebSocket consumers for real-time chat functionality.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat messages.
    """
    
    async def connect(self):
        """Accept WebSocket connection and join conversation room."""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated and is a participant in this conversation
        if not self.user.is_authenticated:
            await self.close()
            return
        
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark messages as read
        await self.mark_messages_as_read()
    
    async def disconnect(self, close_code):
        """Leave conversation room."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return
        
        # Save message to database
        message = await self.save_message(message_content)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'message_id': message.id,
                'created_at': message.created_at.isoformat(),
            }
        )
    
    async def chat_message(self, event):
        """Receive message from room group and send to WebSocket."""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'message_id': event['message_id'],
            'created_at': event['created_at'],
        }))
    
    @database_sync_to_async
    def check_participant(self):
        """Check if user is a participant in this conversation."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return self.user in [conversation.participant1, conversation.participant2]
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database."""
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        # Update conversation's updated_at timestamp
        conversation.save()
        return message
    
    @database_sync_to_async
    def mark_messages_as_read(self):
        """Mark all messages in this conversation as read for the current user."""
        Message.objects.filter(
            conversation_id=self.conversation_id,
            is_read=False
        ).exclude(sender=self.user).update(is_read=True)
