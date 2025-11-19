"""
AI-сервис для анализа задач с использованием Google Gemini API.
"""
import os
import json
import logging
from typing import Optional, Dict
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        # Альтернативный импорт для некоторых версий
        from google import generativeai as genai
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False
        logger.warning("google-generativeai не установлен. AI-функции будут недоступны.")


class AIAnalysisResult:
    """Результат AI-анализа задачи."""
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


def analyze_task_description(user_input: str, language: str = 'ru') -> Optional[AIAnalysisResult]:
    """
    Анализирует описание задачи пользователя с помощью Google Gemini AI.
    
    Args:
        user_input: Текст описания задачи от пользователя
        language: Язык ('ru' или 'uz')
    
    Returns:
        AIAnalysisResult или None в случае ошибки
    """
    if not GEMINI_AVAILABLE:
        logger.error("Gemini API недоступен")
        return None
    
    api_key = getattr(settings, 'GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY'))
    if not api_key:
        logger.error("GEMINI_API_KEY не настроен")
        return None
    
    try:
        # Настройка Gemini
        genai.configure(api_key=api_key)
        # Используем доступную модель
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            # Fallback на стандартную модель
            model = genai.GenerativeModel('gemini-pro')
        
        # Формирование промпта
        lang_instruction = (
            'Vazifani o\'zbek tilida tahlil qiling va javoblarni O\'ZBEK tilida qaytaring.'
            if language == 'uz'
            else 'Проанализируй запрос пользователя и верни структурированные данные на РУССКОМ языке.'
        )
        
        prompt = f"""
Ты помощник сервиса по поиску специалистов (Profi.ru, YouDo).
{lang_instruction}
Пользователь хочет: "{user_input}".

Предложи:
1. Короткий и понятный заголовок задачи (максимум 200 символов).
2. Категорию услуги (например: Ремонт, Сантехника, Уборка, Репетиторы, Красота, Перевозки, IT, Обучение).
3. Улучшенное, профессиональное описание задачи (2-3 предложения).
4. Оценочный диапазон бюджета в рублях (минимальное и максимальное значение).

Верни ответ ТОЛЬКО в формате JSON:
{{
    "suggested_title": "заголовок",
    "suggested_category": "категория",
    "refined_description": "описание",
    "estimated_budget_min": число,
    "estimated_budget_max": число
}}
"""
        
        # Генерация ответа
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 500,
            }
        )
        
        # Парсинг JSON ответа
        response_text = response.text.strip()
        
        # Удаляем markdown code blocks если есть
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        result_data = json.loads(response_text)
        
        return AIAnalysisResult(
            suggested_title=result_data.get('suggested_title', ''),
            suggested_category=result_data.get('suggested_category', 'Разное'),
            refined_description=result_data.get('refined_description', user_input),
            estimated_budget_min=float(result_data.get('estimated_budget_min', 0)),
            estimated_budget_max=float(result_data.get('estimated_budget_max', 0)),
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON от Gemini: {e}")
        logger.error(f"Ответ: {response_text if 'response_text' in locals() else 'N/A'}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при анализе задачи через Gemini: {e}", exc_info=True)
        return None

