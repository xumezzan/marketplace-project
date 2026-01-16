from rest_framework import serializers
from .models import VerificationDocument

class VerificationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDocument
        fields = ('id', 'document_type', 'file', 'status', 'rejection_reason', 'uploaded_at')
        read_only_fields = ('status', 'rejection_reason', 'uploaded_at')

    def create(self, validated_data):
        user = self.context['request'].user
        if user.role != 'SPECIALIST':
            raise serializers.ValidationError("Only specialists can upload verification documents")
        validated_data['specialist'] = user
        return super().create(validated_data)
