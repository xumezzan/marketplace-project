from rest_framework import serializers
from .models import Chat, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.email', read_only=True)
    
    class Meta:
        model = Message
        fields = ('id', 'sender', 'sender_name', 'text', 'created_at', 'is_read')
        read_only_fields = ('sender', 'is_read', 'created_at')

class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ('id', 'deal', 'last_message')
    
    def get_last_message(self, obj):
        last = obj.messages.last()
        if last:
            return MessageSerializer(last).data
        return None
