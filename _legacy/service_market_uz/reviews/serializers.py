from rest_framework import serializers
from .models import Review
from orders.models import Order

class ReviewSerializer(serializers.ModelSerializer):
    client = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ['id', 'order', 'client', 'specialist', 'rating', 'comment', 'created_at']
        read_only_fields = ['client', 'created_at']

    def validate(self, attrs):
        # Ensure the client is the owner of the order
        order = attrs['order']
        user = self.context['request'].user
        
        if order.client != user:
            raise serializers.ValidationError("You can only review your own orders.")
            
        # Ensure the order is completed (optional business rule, but good practice)
        if order.status != Order.Status.COMPLETED:
            raise serializers.ValidationError("You can only review completed orders.")
            
        # Ensure the specialist matches the order's accepted specialist (if we tracked that)
        # For now, we trust the client to pick the right specialist in the form, 
        # or better: we infer it from the order if we stored 'accepted_response' on the order.
        # But our current Order model doesn't explicitly link to the 'winning' specialist directly 
        # except via Response. Let's assume the frontend sends the specialist ID 
        # and we validate it matches the accepted response.
        
        # TODO: Add validation that 'specialist' is indeed the one who performed the order.
        
        return attrs
