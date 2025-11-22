"""
API endpoints for portfolio management.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import PortfolioItem


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reorder_portfolio(request):
    """
    Reorder portfolio items.
    
    Expects: { "items": [{"id": 1, "order": 0}, {"id": 2, "order": 1}, ...] }
    """
    if not request.user.is_specialist:
        return Response(
            {'error': 'Only specialists can reorder portfolio items'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    items_data = request.data.get('items', [])
    
    if not items_data:
        return Response(
            {'error': 'No items provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update order for each item
    updated_count = 0
    for item_data in items_data:
        item_id = item_data.get('id')
        new_order = item_data.get('order')
        
        if item_id is None or new_order is None:
            continue
        
        try:
            item = PortfolioItem.objects.get(id=item_id, specialist=request.user)
            item.order = new_order
            item.save(update_fields=['order'])
            updated_count += 1
        except PortfolioItem.DoesNotExist:
            continue
    
    return Response({
        'success': True,
        'updated': updated_count
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_upload_portfolio(request):
    """
    Handle bulk portfolio image uploads.
    
    Expects multipart/form-data with multiple 'images' files.
    """
    if not request.user.is_specialist:
        return Response(
            {'error': 'Only specialists can upload portfolio items'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    files = request.FILES.getlist('images')
    
    if not files:
        return Response(
            {'error': 'No images provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get the highest current order
    max_order = PortfolioItem.objects.filter(specialist=request.user).count()
    
    created_items = []
    for idx, file in enumerate(files):
        # Create portfolio item with auto-generated title
        item = PortfolioItem.objects.create(
            specialist=request.user,
            title=f"Portfolio Item {max_order + idx + 1}",
            image=file,
            order=max_order + idx
        )
        created_items.append({
            'id': item.id,
            'title': item.title,
            'image_url': item.image.url,
            'order': item.order
        })
    
    return Response({
        'success': True,
        'created': len(created_items),
        'items': created_items
    })
