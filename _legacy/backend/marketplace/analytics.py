"""
Analytics helper functions for specialist dashboard.
"""
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Task, Review, Deal


def get_specialist_stats(specialist):
    """
    Calculate key performance metrics for a specialist.
    
    Returns:
        dict: Statistics including total bookings, revenue, rating, etc.
    """
    # Total bookings
    total_bookings = Booking.objects.filter(specialist=specialist).count()
    completed_bookings = Booking.objects.filter(
        specialist=specialist,
        status=Booking.Status.COMPLETED
    ).count()
    
    # Revenue from completed deals
    total_revenue = Deal.objects.filter(
        specialist=specialist,
        status=Deal.Status.COMPLETED
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Average rating
    avg_rating = Review.objects.filter(
        specialist=specialist
    ).aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Total clients (unique)
    total_clients = Booking.objects.filter(
        specialist=specialist
    ).values('client').distinct().count()
    
    # Active tasks
    active_tasks = Task.objects.filter(
        offers__specialist=specialist,
        status=Task.Status.IN_PROGRESS
    ).distinct().count()
    
    return {
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'total_revenue': float(total_revenue),
        'avg_rating': round(float(avg_rating), 1),
        'total_clients': total_clients,
        'active_tasks': active_tasks,
        'completion_rate': round((completed_bookings / total_bookings * 100) if total_bookings > 0 else 0, 1)
    }


def get_booking_trends(specialist, days=30):
    """
    Get booking trends over the specified period.
    
    Args:
        specialist: Specialist user
        days: Number of days to look back
        
    Returns:
        dict: Daily booking counts
    """
    start_date = timezone.now() - timedelta(days=days)
    
    bookings = Booking.objects.filter(
        specialist=specialist,
        created_at__gte=start_date
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Create a complete date range
    date_range = {}
    current_date = start_date.date()
    end_date = timezone.now().date()
    
    while current_date <= end_date:
        date_range[str(current_date)] = 0
        current_date += timedelta(days=1)
    
    # Fill in actual counts
    for booking in bookings:
        date_range[str(booking['day'])] = booking['count']
    
    return {
        'labels': list(date_range.keys()),
        'data': list(date_range.values())
    }


def get_revenue_data(specialist, days=30):
    """
    Get revenue data over the specified period.
    
    Args:
        specialist: Specialist user
        days: Number of days to look back
        
    Returns:
        dict: Daily revenue amounts
    """
    start_date = timezone.now() - timedelta(days=days)
    
    deals = Deal.objects.filter(
        specialist=specialist,
        status=Deal.Status.COMPLETED,
        updated_at__gte=start_date
    ).extra(
        select={'day': 'date(updated_at)'}
    ).values('day').annotate(revenue=Sum('amount')).order_by('day')
    
    # Create a complete date range
    date_range = {}
    current_date = start_date.date()
    end_date = timezone.now().date()
    
    while current_date <= end_date:
        date_range[str(current_date)] = 0
        current_date += timedelta(days=1)
    
    # Fill in actual revenue
    for deal in deals:
        date_range[str(deal['day'])] = float(deal['revenue'] or 0)
    
    return {
        'labels': list(date_range.keys()),
        'data': list(date_range.values())
    }


def get_top_clients(specialist, limit=5):
    """
    Get top clients by number of bookings.
    
    Args:
        specialist: Specialist user
        limit: Number of top clients to return
        
    Returns:
        list: Top clients with booking counts
    """
    top_clients = Booking.objects.filter(
        specialist=specialist
    ).values(
        'client__id',
        'client__username',
        'client__first_name',
        'client__last_name'
    ).annotate(
        booking_count=Count('id')
    ).order_by('-booking_count')[:limit]
    
    return [
        {
            'id': client['client__id'],
            'name': f"{client['client__first_name']} {client['client__last_name']}".strip() or client['client__username'],
            'booking_count': client['booking_count']
        }
        for client in top_clients
    ]


def get_recent_activity(specialist, limit=10):
    """
    Get recent activity (bookings, reviews, deals).
    
    Args:
        specialist: Specialist user
        limit: Number of recent items to return
        
    Returns:
        list: Recent activity items
    """
    activities = []
    
    # Recent bookings
    recent_bookings = Booking.objects.filter(
        specialist=specialist
    ).select_related('client', 'task').order_by('-created_at')[:limit]
    
    for booking in recent_bookings:
        activities.append({
            'type': 'booking',
            'title': f"New booking from {booking.client.get_full_name() or booking.client.username}",
            'description': booking.task.title if booking.task else 'No task',
            'date': booking.created_at,
            'status': booking.get_status_display()
        })
    
    # Recent reviews
    recent_reviews = Review.objects.filter(
        specialist=specialist
    ).select_related('client').order_by('-created_at')[:limit]
    
    for review in recent_reviews:
        activities.append({
            'type': 'review',
            'title': f"New review from {review.client.get_full_name() or review.client.username}",
            'description': f"Rating: {review.rating}/5",
            'date': review.created_at,
            'status': f"{review.rating} stars"
        })
    
    # Sort by date and limit
    activities.sort(key=lambda x: x['date'], reverse=True)
    return activities[:limit]
