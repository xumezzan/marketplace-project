from .models import Notification

def notifications(request):
    """
    Context processor to add unread notifications count to all templates.
    """
    if request.user.is_authenticated:
        unread_count = request.user.marketplace_notifications.filter(is_read=False).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}
