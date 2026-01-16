import os
import django
import asyncio
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django.conf import settings
if not settings.configured:
    django.setup()

# Override CHANNEL_LAYERS for testing
settings.CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from chat.models import Conversation
from chat.consumers import ChatConsumer

User = get_user_model()

async def test_chat_flow():
    print("Testing Chat Flow...")
    
    # 1. Setup Data
    user1, _ = await database_sync_to_async(User.objects.get_or_create)(username='chat_user1', defaults={'email': 'chat1@test.com', 'password': 'password'})
    user2, _ = await database_sync_to_async(User.objects.get_or_create)(username='chat_user2', defaults={'email': 'chat2@test.com', 'password': 'password'})
    
    conversation = await database_sync_to_async(Conversation.objects.create)()
    await database_sync_to_async(conversation.participants.add)(user1, user2)
    
    print(f"Conversation created: {conversation.id}")
    
    # 2. Connect User 1
    from channels.routing import URLRouter
    from django.urls import re_path
    
    application = URLRouter([
        re_path(r'ws/chat/(?P<conversation_id>\d+)/$', ChatConsumer.as_asgi()),
    ])
    
    communicator1 = WebsocketCommunicator(application, f"/ws/chat/{conversation.id}/")
    communicator1.scope['user'] = user1
    connected1, subprotocol1 = await communicator1.connect()
    assert connected1
    print("User 1 connected")
    
    # 3. Connect User 2
    communicator2 = WebsocketCommunicator(application, f"/ws/chat/{conversation.id}/")
    communicator2.scope['user'] = user2
    connected2, subprotocol2 = await communicator2.connect()
    assert connected2
    print("User 2 connected")
    
    # 4. User 1 sends message
    message_text = "Hello from User 1"
    await communicator1.send_json_to({
        'type': 'chat_message',
        'message': message_text
    })
    print(f"User 1 sent: {message_text}")
    
    # 5. User 2 receives message
    response2 = await communicator2.receive_json_from()
    print(f"User 2 received: {response2}")
    assert response2['message'] == message_text
    assert response2['sender_username'] == 'chat_user1'
    
    # 6. User 1 receives their own message (confirmation)
    response1 = await communicator1.receive_json_from()
    assert response1['message'] == message_text
    
    # 7. Video Call Signal
    await communicator1.send_json_to({
        'type': 'video_call_start'
    })
    print("User 1 started video call")
    
    response_video = await communicator2.receive_json_from()
    assert response_video['type'] == 'video_call_start'
    print("User 2 received video call signal")
    
    await communicator1.disconnect()
    await communicator2.disconnect()
    print("SUCCESS: Chat flow verified!")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_chat_flow())
