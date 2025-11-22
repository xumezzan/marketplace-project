from .models import Notification, NotificationPreference
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def create_notification(user, type, title, message, link=None):
    """
    Create a notification for a user and send email if enabled.
    """
    # Create in-app notification
    notification = Notification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        link=link
    )
    
    # Check preferences and send email
    try:
        prefs = NotificationPreference.objects.get(user=user)
    except NotificationPreference.DoesNotExist:
        prefs = NotificationPreference.objects.create(user=user)
        
    should_send_email = False
    if type == Notification.Type.BOOKING and prefs.email_booking:
        should_send_email = True
    elif type == Notification.Type.MESSAGE and prefs.email_message:
        should_send_email = True
    elif type == Notification.Type.REVIEW and prefs.email_review:
        should_send_email = True
    elif type == Notification.Type.SYSTEM and prefs.email_system:
        should_send_email = True
        
    if should_send_email:
        send_email_notification(user, title, message, link)
        
    return notification

def send_email_notification(user, title, message, link=None):
    """
    Send an email notification.
    """
    subject = f"{settings.EMAIL_SUBJECT_PREFIX} {title}"
    html_message = render_to_string('marketplace/emails/notification.html', {
        'user': user,
        'title': title,
        'message': message,
        'link': link,
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send email: {e}")
