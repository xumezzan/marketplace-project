from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from ..models import Category, Task
from ..serializers import SpecialistSerializer, CategorySerializer, TaskSerializer

User = get_user_model()

@api_view(['GET'])
def search_suggestions(request):
    """
    Returns search suggestions for specialists, categories, and tasks.
    GET /api/search/suggestions/?q=query
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return Response({'results': []})
    
    # Search specialists
    specialists = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query),
        is_specialist=True
    ).select_related('specialist_profile')[:5]
    
    # Search categories
    categories = Category.objects.filter(
        Q(name__icontains=query)
    )[:5]
    
    # Search tasks
    tasks = Task.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        status=Task.Status.PUBLISHED
    ).select_related('category')[:5]
    
    return Response({
        'specialists': SpecialistSerializer(specialists, many=True).data,
        'categories': CategorySerializer(categories, many=True).data,
        'tasks': TaskSerializer(tasks, many=True).data,
    })
