"""
Context processors for marketplace app.
"""
from .models import Notification


def unread_notifications(request):
    """
    Add unread notifications count to template context.
    """
    if request.user.is_authenticated:
        try:
            unread_count = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
        except Exception:
            unread_count = 0
    else:
        unread_count = 0
    
    return {
        'unread_notifications_count': unread_count,
    }
