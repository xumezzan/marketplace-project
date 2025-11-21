"""
AI Service Layer для Services Marketplace

Интеграция с Google Gemini API для:
- Парсинг свободного текста в структурированную задачу
- Оценка стоимости услуг
- Ранжирование задач для специалистов
- Подбор оптимального расписания
"""

import json
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.db.models import QuerySet

logger = logging.getLogger(__name__)

# Проверяем наличие Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = bool(settings.GEMINI_API_KEY)
    if GEMINI_AVAILABLE:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Используем Gemini 1.5 Flash для быстрых ответов
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            model = genai.GenerativeModel('gemini-pro')
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai не установлен. AI-функции будут использовать fallback логику.")


class AIAnalysisResult:
    """Результат AI-анализа задачи (для обратной совместимости)."""
    def __init__(self, suggested_title: str, suggested_category: str, 
                 refined_description: str, estimated_budget_min: float,
                 estimated_budget_max: float):
        self.suggested_title = suggested_title
        self.suggested_category = suggested_category
        self.refined_description = refined_description
        self.estimated_budget_min = estimated_budget_min
        self.estimated_budget_max = estimated_budget_max
    
    def to_dict(self) -> Dict:
        """Преобразует результат в словарь."""
        return {
            'suggested_title': self.suggested_title,
            'suggested_category': self.suggested_category,
            'refined_description': self.refined_description,
            'estimated_budget_min': self.estimated_budget_min,
            'estimated_budget_max': self.estimated_budget_max,
        }


class AIService:
    """
    Сервис для работы с AI функциями.
    
    Использует Google Gemini API если доступен, иначе fallback на простую логику.
    """
    
    @staticmethod
    def is_available() -> bool:
        """Проверка доступности AI сервиса."""
        return GEMINI_AVAILABLE
    
    @staticmethod
    def parse_task_text(text: str, user=None) -> Dict[str, Any]:
        """
        Парсинг свободного текста в структурированную задачу.
        
        Args:
            text: Свободный текст от пользователя
            user: Пользователь (для логирования)
            
        Returns:
            dict с полями:
                - category_id: int или None
                - subcategory_id: int или None
                - title: str
                - description: str
                - format: str (online/offline/at_specialist)
                - budget_min: float или None
                - budget_max: float или None
                - city: str или None
                - preferred_date: str (ISO format) или None
                - requirements: list[str]
        """
        if not text or len(text.strip()) < 10:
            return {
                'error': 'Текст слишком короткий',
                'title': text[:100] if text else '',
                'description': text
            }
        
        if GEMINI_AVAILABLE:
            return AIService._parse_with_gemini(text, user)
        else:
            return AIService._parse_fallback(text)
    
    @staticmethod
    def _parse_with_gemini(text: str, user=None) -> Dict[str, Any]:
        """Парсинг с использованием Gemini API."""
        from backend.marketplace.models import Category, Subcategory
        
        # Получаем список категорий для контекста
        categories = list(Category.objects.values('id', 'name'))
        categories_text = "\n".join([f"- {c['name']} (id: {c['id']})" for c in categories])
        
        prompt = f"""
Ты - AI ассистент для маркетплейса услуг. Проанализируй запрос пользователя и извлеки структурированную информацию.

ДОСТУПНЫЕ КАТЕГОРИИ:
{categories_text}

ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
{text}

ИНСТРУКЦИИ:
1. Определи наиболее подходящую категорию из списка выше
2. Сформулируй краткий заголовок (до 100 символов)
3. Составь подробное описание задачи
4. Определи формат: "online" (онлайн), "offline" (выезд к клиенту), "at_specialist" (у специалиста)
5. Извлеки бюджет если указан (минимум и максимум)
6. Извлеки город если указан
7. Извлеки желаемую дату если указана
8. Составь список ключевых требований

ОТВЕТЬ СТРОГО В ФОРМАТЕ JSON (без markdown блоков):
{{
  "category_id": <id категории или null>,
  "title": "<краткий заголовок>",
  "description": "<подробное описание>",
  "format": "<online|offline|at_specialist>",
  "budget_min": <число или null>,
  "budget_max": <число или null>,
  "city": "<город или null>",
  "preferred_date": "<YYYY-MM-DD или null>",
  "requirements": ["<требование 1>", "<требование 2>"]
}}
"""
        
        try:
            # Логируем запрос
            AIService._log_request('parse', {'text': text[:500]}, user)
            
            # Отправляем запрос к Gemini
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Убираем markdown блоки если есть
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            # Парсим JSON
            result = json.loads(result_text)
            
            # Логируем успешный ответ
            AIService._log_request('parse', {'text': text[:500]}, user, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге с Gemini: {e}")
            # Fallback на простую логику
            return AIService._parse_fallback(text)
    
    @staticmethod
    def _parse_fallback(text: str) -> Dict[str, Any]:
        """Простая логика парсинга без AI."""
        import re
        from backend.marketplace.models import Category
        
        result = {
            'category_id': None,
            'title': text[:100],
            'description': text,
            'format': 'offline',
            'budget_min': None,
            'budget_max': None,
            'city': None,
            'preferred_date': None,
            'requirements': []
        }
        
        # Простое определение категории по ключевым словам
        text_lower = text.lower()
        keywords_map = {
            'репетитор': ['репетитор', 'учитель', 'обучение', 'занятия'],
            'ремонт': ['ремонт', 'починить', 'отремонтировать', 'мастер'],
            'уборка': ['уборка', 'убрать', 'клининг', 'чистка'],
            'красота': ['маникюр', 'педикюр', 'стрижка', 'макияж'],
        }
        
        for category_name, keywords in keywords_map.items():
            if any(kw in text_lower for kw in keywords):
                try:
                    category = Category.objects.filter(name__icontains=category_name).first()
                    if category:
                        result['category_id'] = category.id
                        break
                except Exception:
                    pass
        
        # Поиск цен (числа + валюта)
        price_pattern = r'(\d+[\s,]?\d*)\s*(сум|руб|₽|$|долл)'
        prices = re.findall(price_pattern, text_lower)
        if prices:
            numbers = [int(p[0].replace(' ', '').replace(',', '')) for p in prices]
            result['budget_min'] = min(numbers)
            result['budget_max'] = max(numbers)
        
        # Поиск городов
        cities = ['ташкент', 'москва', 'самарканд', 'бухара']
        for city in cities:
            if city in text_lower:
                result['city'] = city.capitalize()
                break
        
        # Определение формата
        if 'онлайн' in text_lower or 'online' in text_lower:
            result['format'] = 'online'
        
        return result
    
    @staticmethod
    def estimate_price(task_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Оценка примерной стоимости услуги.
        
        Args:
            task_data: данные задачи (category, subcategory, description, etc.)
            
        Returns:
            dict с полями:
                - estimated_min: минимальная оценка
                - estimated_max: максимальная оценка
                - confidence: уверенность (0.0 - 1.0)
        """
        from backend.marketplace.models import Deal, Task
        from django.db.models import Avg
        
        category_id = task_data.get('category_id')
        
        if not category_id:
            return {
                'estimated_min': 0,
                'estimated_max': 0,
                'confidence': 0.0
            }
        
        # Получаем статистику по завершенным сделкам в этой категории
        completed_deals = Deal.objects.filter(
            task__category_id=category_id,
            status=Deal.Status.COMPLETED
        )
        
        if completed_deals.exists():
            avg_price = completed_deals.aggregate(avg=Avg('final_price'))['avg']
            # Диапазон ±30% от средней цены
            estimated_min = avg_price * 0.7
            estimated_max = avg_price * 1.3
            confidence = min(completed_deals.count() / 10, 1.0)  # макс уверенность при 10+ сделках
        else:
            # Нет данных - используем дефолтные значения по категории
            estimated_min = 50000  # 50k сум
            estimated_max = 200000  # 200k сум
            confidence = 0.1
        
        return {
            'estimated_min': round(estimated_min, -3),  # округляем до тысяч
            'estimated_max': round(estimated_max, -3),
            'confidence': round(confidence, 2)
        }
    
    @staticmethod
    def rank_tasks_for_specialist(specialist, tasks: QuerySet) -> List[int]:
        """
        Ранжирование задач для специалиста по релевантности.
        
        Args:
            specialist: User объект специалиста
            tasks: QuerySet задач
            
        Returns:
            list[int]: список ID задач в порядке убывания релевантности
        """
        if not tasks.exists():
            return []
        
        try:
            profile = specialist.specialist_profile
        except Exception:
            # Нет профиля специалиста
            return list(tasks.values_list('id', flat=True))
        
        scored_tasks = []
        
        for task in tasks:
            score = 0
            
            # 1. Совпадение категории (+50 баллов)
            if task.category in profile.categories.all():
                score += 50
            
            # 2. Совпадение формата (+30 баллов)
            if task.format == 'online' and profile.works_online:
                score += 30
            elif task.format == 'offline':
                # Проверяем расстояние (упрощенно - по городу)
                if task.city == specialist.city:
                    score += 30
            
            # 3. Бюджет в пределах тарифов (+20 баллов)
            if task.budget_min and profile.hourly_rate:
                if task.budget_min >= profile.hourly_rate:
                    score += 20
            
            # 4. Свежесть задачи (+10 баллов за последние 24ч)
            from django.utils import timezone
            from datetime import timedelta
            if task.created_at > timezone.now() - timedelta(days=1):
                score += 10
            
            scored_tasks.append((task.id, score))
        
        # Сортируем по убыванию score
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        
        return [task_id for task_id, score in scored_tasks]
    
    @staticmethod
    def _log_request(request_type: str, input_data: Dict, user=None, output_data: Dict = None):
        """Логирование AI запроса в базу данных."""
        try:
            from backend.marketplace.models import AIRequest
            AIRequest.objects.create(
                user=user,
                request_type=request_type,
                input_data=input_data,
                output_data=output_data or {},
                model_used='gemini-1.5-flash' if GEMINI_AVAILABLE else 'fallback'
            )
        except Exception as e:
            logger.error(f"Ошибка логирования AI запроса: {e}")


# Старая функция для обратной совместимости
def analyze_task_description(user_input: str, language: str = 'ru') -> Optional[AIAnalysisResult]:
    """
    Legacy функция для анализа задачи.
    
    Args:
        user_input: Текст описания задачи
        language: Язык
        
    Returns:
        AIAnalysisResult или None
    """
    result = AIService.parse_task_text(user_input)
    
    if result.get('error'):
        return None
    
    return AIAnalysisResult(
        suggested_title=result.get('title', ''),
        suggested_category=result.get('category_id', 'Разное'),
        refined_description=result.get('description', user_input),
        estimated_budget_min=result.get('budget_min', 0) or 0,
        estimated_budget_max=result.get('budget_max', 0) or 0,
    )
