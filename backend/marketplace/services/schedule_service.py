"""
Сервис для работы с расписанием специалистов.
"""
import datetime
from typing import List, Optional
from django.utils import timezone
from django.db import transaction
from marketplace.models import TimeSlot, SpecialistProfile

class ScheduleService:
    """
    Сервис для управления расписанием.
    """
    
    @staticmethod
    def generate_slots(specialist, start_date: datetime.date, days: int = 30) -> List[TimeSlot]:
        """
        Генерирует слоты для специалиста на указанный период.
        
        Args:
            specialist: User объект специалиста
            start_date: Дата начала генерации
            days: Количество дней
            
        Returns:
            List[TimeSlot]: Список созданных слотов
        """
        try:
            profile = specialist.specialist_profile
        except Exception:
            return []
            
        if not profile.working_days or not profile.working_hours_start or not profile.working_hours_end:
            return []
            
        created_slots = []
        
        # Маппинг дней недели (0=mon, 6=sun)
        weekdays_map = {
            0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'
        }
        
        # Длительность слота (по умолчанию 1 час)
        slot_duration = datetime.timedelta(hours=1)
        
        with transaction.atomic():
            for i in range(days):
                current_date = start_date + datetime.timedelta(days=i)
                weekday_str = weekdays_map.get(current_date.weekday())
                
                # Проверяем, рабочий ли это день
                if weekday_str not in profile.working_days:
                    continue
                
                # Генерируем слоты на день
                current_time = datetime.datetime.combine(current_date, profile.working_hours_start)
                end_time = datetime.datetime.combine(current_date, profile.working_hours_end)
                
                while current_time + slot_duration <= end_time:
                    slot_start = current_time.time()
                    slot_end = (current_time + slot_duration).time()
                    
                    # Проверяем, существует ли уже такой слот
                    exists = TimeSlot.objects.filter(
                        specialist=specialist,
                        date=current_date,
                        time_start=slot_start
                    ).exists()
                    
                    if not exists:
                        slot = TimeSlot.objects.create(
                            specialist=specialist,
                            date=current_date,
                            time_start=slot_start,
                            time_end=slot_end,
                            is_available=True
                        )
                        created_slots.append(slot)
                    
                    current_time += slot_duration
                    
        return created_slots

    @staticmethod
    def get_available_slots(specialist, date: datetime.date) -> List[TimeSlot]:
        """Возвращает свободные слоты специалиста на конкретную дату."""
        return TimeSlot.objects.filter(
            specialist=specialist,
            date=date,
            is_available=True
        ).order_by('time_start')

    @staticmethod
    def book_slot(slot_id: int, deal) -> bool:
        """
        Бронирует слот под сделку.
        
        Args:
            slot_id: ID слота
            deal: Объект сделки
            
        Returns:
            bool: Успешно ли забронировано
        """
        try:
            with transaction.atomic():
                slot = TimeSlot.objects.select_for_update().get(id=slot_id)
                if not slot.is_available:
                    return False
                
                slot.is_available = False
                slot.deal = deal
                slot.save()
                return True
        except TimeSlot.DoesNotExist:
            return False
