from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from ..models import Availability, Booking, Task
from datetime import datetime, timedelta

User = get_user_model()

@api_view(['GET'])
def get_availability(request, specialist_id):
    """
    Returns available dates and slots for a specialist in a given month.
    GET /api/specialist/{id}/availability/?year=2023&month=11
    """
    specialist = get_object_or_404(User, id=specialist_id, is_specialist=True)
    
    # If date is provided, return slots for that specific date
    date_str = request.GET.get('date')
    if date_str:
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            day_of_week = query_date.weekday()
            
            # Get availability rules for this day of week
            rules = availability_slots.filter(day_of_week=day_of_week)
            
            # Get existing bookings for this date
            existing_bookings = Booking.objects.filter(
                specialist=specialist,
                scheduled_date=query_date,
                status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED]
            )
            booked_times = [b.scheduled_time.strftime('%H:%M') for b in existing_bookings]
            
            slots = []
            for rule in rules:
                # Generate 1-hour slots (simple implementation)
                current_time = datetime.combine(query_date, rule.start_time)
                end_time = datetime.combine(query_date, rule.end_time)
                
                while current_time + timedelta(hours=1) <= end_time:
                    time_str = current_time.time().strftime('%H:%M')
                    if time_str not in booked_times:
                        slots.append(time_str)
                    current_time += timedelta(hours=1)
            
            return Response({'slots': sorted(slots)})
            
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        year = int(request.GET.get('year', datetime.now().year))
        month = int(request.GET.get('month', datetime.now().month))
    except ValueError:
        return Response({'error': 'Invalid date parameters'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get recurring availability
    availability_slots = Availability.objects.filter(specialist=specialist)
    
    # Generate dates for the month
    num_days = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day
    available_dates = []
    
    for day in range(1, num_days + 1):
        date = datetime(year, month, day).date()
        day_of_week = date.weekday() # 0=Mon, 6=Sun
        
        # Check if specialist works on this day of week
        if availability_slots.filter(day_of_week=day_of_week).exists():
            available_dates.append(date.strftime('%Y-%m-%d'))
            
    return Response({
        'dates': available_dates
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    """
    Creates a new booking.
    POST /api/bookings/create/
    Data: { task_id, specialist_id, date, time, notes }
    """
    data = request.data
    user = request.user
    
    if not user.is_client:
        return Response({'error': 'Only clients can create bookings'}, status=status.HTTP_403_FORBIDDEN)
        
    try:
        task = Task.objects.get(id=data.get('task_id'), client=user)
        specialist = User.objects.get(id=data.get('specialist_id'), is_specialist=True)
        date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        time = datetime.strptime(data.get('time'), '%H:%M').time()
        
        # Check if slot is free (simple check)
        if Booking.objects.filter(specialist=specialist, scheduled_date=date, scheduled_time=time).exists():
             return Response({'error': 'This slot is already booked'}, status=status.HTTP_409_CONFLICT)
             
        booking = Booking.objects.create(
            task=task,
            specialist=specialist,
            client=user,
            scheduled_date=date,
            scheduled_time=time,
            notes=data.get('notes', '')
        )
        
        return Response({'id': booking.id, 'status': 'success'}, status=status.HTTP_201_CREATED)
        
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'Specialist not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
