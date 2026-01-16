from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_specialist_rating(sender, instance, **kwargs):
    """
    Recalculate specialist's average rating and review count
    whenever a review is saved or deleted.
    """
    specialist = instance.specialist
    
    # Check if specialist has a profile
    if hasattr(specialist, 'specialist_profile'):
        profile = specialist.specialist_profile
        
        # Calculate aggregates
        aggregates = Review.objects.filter(specialist=specialist).aggregate(
            avg_rating=Avg('rating'),
            count=models.Count('id')
        )
        
        profile.rating = aggregates['avg_rating'] or 0.0
        profile.review_count = aggregates['count'] or 0
        profile.save()
