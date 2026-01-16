from rest_framework import serializers
from .models import Deal

class DealSerializer(serializers.ModelSerializer):
    specialist_name = serializers.CharField(source='specialist.specialist_profile.user.email', read_only=True)
    specialist_phone = serializers.SerializerMethodField()
    client_phone = serializers.SerializerMethodField()

    class Meta:
        model = Deal
        fields = '__all__'
        read_only_fields = ('request', 'specialist', 'status', 'created_at', 'contacts_shared_at')

    def get_specialist_phone(self, obj):
        if obj.contacts_shared_at:
            return obj.specialist.phone
        return None

    def get_client_phone(self, obj):
        if obj.contacts_shared_at:
            return obj.request.client.phone
        return None
