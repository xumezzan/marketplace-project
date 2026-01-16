from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer
from .signals import update_specialist_rating

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        review = serializer.save()
        update_specialist_rating(review.specialist)
