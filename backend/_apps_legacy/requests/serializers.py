from rest_framework import serializers
from .models import Request

class RequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.first_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = Request
        fields = (
            'id', 'client', 'client_name', 'category', 'category_name', 
            'district', 'district_name', 'budget', 'description', 
            'status', 'created_at'
        )
        read_only_fields = ('client', 'status', 'created_at')

    def create(self, validated_data):
        user = self.context['request'].user
        if user.role != 'CLIENT':
            raise serializers.ValidationError("Only clients can create requests")
        validated_data['client'] = user
        return super().create(validated_data)
