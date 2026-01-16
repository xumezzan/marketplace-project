from rest_framework import serializers
from .models import User, ClientProfile, SpecialistProfile, PortfolioItem

class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['id', 'title', 'description', 'image', 'created_at']
        read_only_fields = ['created_at']

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['full_name', 'avatar', 'city']

class SpecialistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistProfile
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = SpecialistProfile
        fields = ['bio', 'rating', 'review_count', 'is_verified', 'telegram_username', 'portfolio_links', 'portfolio_items']

class UserSerializer(serializers.ModelSerializer):
    client_profile = ClientProfileSerializer(read_only=True)
    specialist_profile = SpecialistProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'email', 'role', 'client_profile', 'specialist_profile']
        read_only_fields = ['id']
