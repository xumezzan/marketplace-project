from rest_framework import serializers
from .models import Response

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = '__all__'
        read_only_fields = ('specialist', 'tariff_type', 'price_paid', 'status', 'viewed_at_by_client', 'refund_processed')

class CreateResponseSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True)
