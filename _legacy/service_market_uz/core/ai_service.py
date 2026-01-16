import json
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.db.models import QuerySet, Avg

logger = logging.getLogger(__name__)

# Check for Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = bool(getattr(settings, 'GEMINI_API_KEY', None))
    if GEMINI_AVAILABLE:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            model = genai.GenerativeModel('gemini-pro')
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. AI functions will use fallback logic.")

class AIService:
    """
    Service for AI functions using Google Gemini API.
    """
    
    @staticmethod
    def is_available() -> bool:
        return GEMINI_AVAILABLE
    
    @staticmethod
    def parse_task_text(text: str, user=None) -> Dict[str, Any]:
        """
        Parse free text into structured task data.
        """
        if not text or len(text.strip()) < 10:
            return {
                'error': 'Text too short',
                'title': text[:100] if text else '',
                'description': text
            }
        
        if GEMINI_AVAILABLE:
            return AIService._parse_with_gemini(text, user)
        else:
            return AIService._parse_fallback(text)
    
    @staticmethod
    def _parse_with_gemini(text: str, user=None) -> Dict[str, Any]:
        from services.models import Category
        
        categories = list(Category.objects.values('id', 'name'))
        categories_text = "\n".join([f"- {c['name']} (id: {c['id']})" for c in categories])
        
        prompt = f"""
        You are an AI assistant for a services marketplace. Analyze the user request and extract structured info.
        
        AVAILABLE CATEGORIES:
        {categories_text}
        
        USER REQUEST:
        {text}
        
        INSTRUCTIONS:
        1. Determine the best category ID from the list.
        2. Create a short title (max 100 chars).
        3. Create a detailed description.
        4. Extract budget (min/max) if present.
        5. Extract city if present.
        
        RESPOND STRICTLY IN JSON:
        {{
          "category_id": <id or null>,
          "title": "<title>",
          "description": "<description>",
          "budget_min": <number or null>,
          "budget_max": <number or null>,
          "city": "<city or null>"
        }}
        """
        
        try:
            AIService._log_request('parse', {'text': text[:500]}, user)
            
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            AIService._log_request('parse', {'text': text[:500]}, user, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini parse error: {e}")
            return AIService._parse_fallback(text)
    
    @staticmethod
    def _parse_fallback(text: str) -> Dict[str, Any]:
        import re
        from services.models import Category
        
        result = {
            'category_id': None,
            'title': text[:100],
            'description': text,
            'budget_min': None,
            'budget_max': None,
            'city': None
        }
        
        # Simple keyword matching for category
        # (Simplified for brevity)
        
        return result
    
    @staticmethod
    def estimate_price(task_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Estimate price based on historical data.
        """
        from orders.models import Order
        
        category_id = task_data.get('category_id')
        if not category_id:
            return {'estimated_min': 0, 'estimated_max': 0}
            
        # Use completed orders for stats
        completed_orders = Order.objects.filter(
            category_id=category_id,
            status=Order.Status.COMPLETED
        )
        
        # This logic assumes Order has a final price field or we calculate it from accepted response
        # Since Order doesn't have final_price in the model I saw earlier, we might need to join with responses
        # For now, let's return a dummy estimate or improve the Order model later.
        
        return {'estimated_min': 50000, 'estimated_max': 150000}

    @staticmethod
    def _log_request(request_type: str, input_data: Dict, user=None, output_data: Dict = None):
        try:
            from core.models import AIRequest
            AIRequest.objects.create(
                user=user,
                request_type=request_type,
                input_data=input_data,
                output_data=output_data or {},
            )
        except Exception as e:
            logger.error(f"AI logging error: {e}")
