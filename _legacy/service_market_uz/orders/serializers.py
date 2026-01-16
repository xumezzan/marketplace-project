from rest_framework import serializers
from .models import Order, OrderResponse
from services.models import Category

from django.contrib.gis.geos import Point

class OrderSerializer(serializers.ModelSerializer):
    client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    response_count = serializers.IntegerField(source='responses.count', read_only=True)
    
    # Custom fields for input (lat/lon)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = [
            'id', 'client', 'category', 'description', 
            'price_from', 'price_to', 'status', 'deadline', 
            'address', 'location', 'latitude', 'longitude',
            'created_at', 'response_count'
        ]
        read_only_fields = ['status', 'created_at', 'location']

    def validate(self, attrs):
        # Convert lat/lon to Point
        lat = attrs.pop('latitude', None)
        lon = attrs.pop('longitude', None)
        
        if lat is not None and lon is not None:
            attrs['location'] = Point(lon, lat, srid=4326)
            
        return attrs


class OrderResponseSerializer(serializers.ModelSerializer):
    specialist = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = OrderResponse
        fields = ['id', 'specialist', 'order', 'price_proposal', 'message', 'is_accepted', 'created_at']
        read_only_fields = ['is_accepted', 'created_at']

    def validate(self, attrs):
        # Check if specialist already responded
        user = self.context['request'].user
        order = attrs['order']
        if OrderResponse.objects.filter(order=order, specialist=user).exists():
            raise serializers.ValidationError("You have already responded to this order.")
        
        # Check if user is a specialist
        if user.role != 'specialist':
             raise serializers.ValidationError("Only specialists can respond to orders.")
             
        return attrs
