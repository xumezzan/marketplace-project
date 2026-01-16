from django.db import models
from django.db.models import Avg

def update_specialist_rating(specialist):
    avg = specialist.reviews_received.aggregate(Avg('rating'))['rating__avg']
    if avg is not None:
        profile = specialist.specialist_profile
        profile.rating = round(avg, 2)
        profile.save(update_fields=['rating'])
