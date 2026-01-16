from django.contrib.auth import get_user_model
from .models import Review

User = get_user_model()

def get_comparison_data(specialist_ids):
    """
    Get comparison data for a list of specialist IDs.
    """
    specialists = User.objects.filter(
        id__in=specialist_ids, 
        is_specialist=True
    ).select_related('specialist_profile')
    
    comparison_data = []
    
    for specialist in specialists:
        profile = specialist.specialist_profile
        
        # Calculate stats
        reviews_count = specialist.reviews_received.count()
        completed_tasks = specialist.deals_as_specialist.filter(status='completed').count()
        
        data = {
            'id': specialist.id,
            'user': specialist,
            'name': specialist.get_full_name() or specialist.username,
            'avatar': specialist.avatar.url if specialist.avatar else None,
            'rating': specialist.rating,
            'reviews_count': reviews_count,
            'hourly_rate': profile.hourly_rate,
            'experience': profile.experience,
            'completed_tasks': completed_tasks,
            'categories': [c.name for c in profile.categories.all()],
            'description': profile.description,
            'is_verified': profile.is_verified,
        }
        comparison_data.append(data)
        
    return comparison_data
