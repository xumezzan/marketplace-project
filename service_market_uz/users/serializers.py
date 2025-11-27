from rest_framework import serializers
from .models import User, ClientProfile, SpecialistProfile

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['full_name', 'avatar', 'city']

class SpecialistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistProfile
        fields = ['bio', 'rating', 'review_count', 'is_verified', 'telegram_username', 'portfolio_links']

class UserSerializer(serializers.ModelSerializer):
    client_profile = ClientProfileSerializer(read_only=True)
    specialist_profile = SpecialistProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'email', 'role', 'client_profile', 'specialist_profile']
        read_only_fields = ['id']
