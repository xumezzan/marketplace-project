from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ClientProfile, SpecialistProfile

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'phone', 'password', 'role')

    def validate_role(self, value):
        if value not in [User.Role.CLIENT, User.Role.SPECIALIST]:
            raise serializers.ValidationError("Invalid role for registration")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        if user.role == User.Role.CLIENT:
            ClientProfile.objects.create(user=user)
        elif user.role == User.Role.SPECIALIST:
            SpecialistProfile.objects.create(user=user)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'role')
