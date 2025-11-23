import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user is a participant
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
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
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
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
                }
            )
        elif message_type == 'video_call_start':
            # Broadcast video call start
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_call_start',
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                }
            )
            await self.set_video_call_status(True)

    # Receive message from room group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'message_id': event['message_id'],
            'created_at': event['created_at'],
        }))
        
    async def video_call_start(self, event):
        await self.send(text_data=json.dumps({
            'type': 'video_call_start',
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
        }))

    @database_sync_to_async
    def check_participant(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participants.filter(id=self.user.id).exists()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            text=content
        )
        conversation.save() # Update updated_at
        return message

    @database_sync_to_async
    def mark_messages_as_read(self):
        Message.objects.filter(
            conversation_id=self.conversation_id,
            is_read=False
        ).exclude(sender=self.user).update(is_read=True)
        
    @database_sync_to_async
    def set_video_call_status(self, status):
        Conversation.objects.filter(id=self.conversation_id).update(video_call_started=status)
