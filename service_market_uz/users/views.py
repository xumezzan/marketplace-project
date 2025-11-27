from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .models import User, ClientProfile
from .serializers import UserSerializer
import redis
import random
import logging

logger = logging.getLogger(__name__)

# Connect to Redis
r = redis.from_url(settings.CELERY_BROKER_URL) # Reusing the same Redis instance

class AuthViewSet(viewsets.ViewSet):
    """
    Authentication ViewSet for SMS OTP flow.
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='send-otp')
    def send_otp(self, request):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response({'error': _('Phone number is required')}, status=status.HTTP_400_BAD_REQUEST)

        # Rate limiting (Simple implementation)
        # Key: otp_rate_limit:{phone_number}
        # Limit: 3 requests per 60 seconds
        rate_key = f"otp_rate_limit:{phone_number}"
        attempts = r.incr(rate_key)
        if attempts == 1:
            r.expire(rate_key, 60)
            
        if attempts > 3:
            return Response({'error': _('Too many requests. Please try again later.')}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate 4-digit code
        code = str(random.randint(1000, 9999))
        
        # Store in Redis with 2 minute TTL
        otp_key = f"otp:{phone_number}"
        r.setex(otp_key, 120, code)
        
        # In production, send SMS here via provider
        # For dev, print to console
        print(f"========================================")
        print(f"SMS CODE FOR {phone_number}: {code}")
        print(f"========================================")
        
        return Response({'message': _('OTP sent successfully')})

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        
        if not phone_number or not code:
            return Response({'error': _('Phone number and code are required')}, status=status.HTTP_400_BAD_REQUEST)
            
        # Verify Code
        otp_key = f"otp:{phone_number}"
        stored_code = r.get(otp_key)
        
        if not stored_code or stored_code.decode('utf-8') != code:
            return Response({'error': _('Invalid or expired code')}, status=status.HTTP_400_BAD_REQUEST)
            
        # Code is valid, delete it
        r.delete(otp_key)
        
        # Get or Create User
        user, created = User.objects.get_or_create(phone_number=phone_number)
        
        if created:
            user.set_unusable_password()
            user.save()
            # ClientProfile is created via signals
            
        # Generate Tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'is_new_user': created
        })
