from celery import shared_task
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from telegram import Bot
import asyncio
from .models import Order
from users.models import User

@shared_task
def notify_specialists_task(order_id):
    """
    Find relevant specialists and send them a Telegram notification.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    if not settings.TELEGRAM_BOT_TOKEN:
        return

    # Find specialists:
    # 1. Active
    # 2. Have telegram_chat_id
    # 3. Subscribed to category
    # 4. Within 10km radius (if order has location)
    
    specialists = User.objects.filter(
        role='specialist',
        is_active=True,
        telegram_chat_id__isnull=False,
        specialist_profile__categories=order.category
    )
    
    if order.location:
        # Filter by distance (e.g., 10km)
        # Note: This requires the specialist to have a location set in their profile
        specialists = specialists.filter(specialist_profile__location__isnull=False).annotate(
            distance=Distance('specialist_profile__location', order.location)
        ).filter(distance__lte=10000) # 10km in meters

    # Send messages
    # Note: In production, you might want to batch this or use a separate task per user to avoid blocking
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    message = (
        f"🔔 <b>New Order!</b>\n\n"
        f"<b>{order.category.name}</b>\n"
        f"{order.description[:100]}...\n\n"
        f"💰 Budget: {order.price_from or 'Negotiable'} - {order.price_to or ''}\n"
        f"📍 Location: {order.address}\n\n"
        f"Apply now via the app!"
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for specialist in specialists:
        try:
            loop.run_until_complete(bot.send_message(chat_id=specialist.telegram_chat_id, text=message, parse_mode='HTML'))
        except Exception as e:
            print(f"Failed to send to {specialist.phone_number}: {e}")
            
    loop.close()
