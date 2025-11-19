import os
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from marketplace.models import SpecialistProfile, TimeSlot
from marketplace.services.schedule_service import ScheduleService

User = get_user_model()

def test_schedule():
    print("--- Testing Schedule System ---")
    
    # 1. Create or get a specialist
    username = 'test_specialist_schedule'
    email = 'schedule@example.com'
    password = 'password123'
    
    try:
        user = User.objects.get(username=username)
        print(f"User {username} already exists.")
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_specialist = True
        user.save()
        print(f"Created user {username}.")
        
    # 2. Setup profile
    profile, created = SpecialistProfile.objects.get_or_create(user=user)
    profile.working_days = ['mon', 'wed', 'fri']
    profile.working_hours_start = datetime.time(9, 0)
    profile.working_hours_end = datetime.time(12, 0) # 3 hours = 3 slots
    profile.save()
    print(f"Updated profile for {username}: Mon, Wed, Fri 09:00-12:00")
    
    # 3. Generate slots
    print("Generating slots...")
    start_date = timezone.now().date()
    # Ensure start_date is a Monday for consistent testing, or just generate for enough days
    # Let's just generate for 7 days
    slots = ScheduleService.generate_slots(user, start_date, days=7)
    print(f"Generated {len(slots)} slots.")
    
    # 4. Verify slots
    all_slots = TimeSlot.objects.filter(specialist=user, date__gte=start_date)
    print(f"Total slots in DB: {all_slots.count()}")
    
    for slot in all_slots[:5]:
        print(f"- {slot}")
        
    # 5. Test booking (mock)
    if all_slots.exists():
        slot_to_book = all_slots.first()
        print(f"Attempting to book slot: {slot_to_book}")
        # We don't have a deal here, so we'll just pass None or mock it if strictly required, 
        # but the service expects a deal object usually. 
        # Let's just check if we can update it manually via service logic
        
        # Create a dummy deal if needed, or just test the logic
        # For now, let's just verify availability toggle
        success = ScheduleService.book_slot(slot_to_book.id, None)
        print(f"Booking result: {success}")
        
        slot_to_book.refresh_from_db()
        print(f"Slot status after booking: is_available={slot_to_book.is_available}")
        
    print("--- Test Finished ---")

if __name__ == '__main__':
    test_schedule()
