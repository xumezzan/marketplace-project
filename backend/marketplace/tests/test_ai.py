from django.test import TestCase
from unittest.mock import patch, MagicMock
from marketplace.services.ai_service import AIService

class AIServiceTest(TestCase):
    def test_parse_fallback(self):
        """Test the fallback parsing logic (no AI)."""
        text = "Нужен репетитор по математике в Ташкенте, бюджет 100000 сум"
        result = AIService._parse_fallback(text)
        
        self.assertEqual(result['city'], 'Ташкент')
        self.assertIn('100000', str(result['budget_min']) if result['budget_min'] else '')
        # Note: category_id might be None if categories aren't in DB, so we skip that check or create category first
        
    def test_parse_with_gemini(self):
        """Test the Gemini parsing logic with mocked API."""
        # Mock the google module and its classes
        mock_genai = MagicMock()
        mock_model_class = MagicMock()
        mock_genai.GenerativeModel = mock_model_class
        
        # Setup the mock response
        mock_model = mock_model_class.return_value
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "category_id": 1,
            "title": "Репетитор по математике",
            "description": "Нужен репетитор",
            "format": "online",
            "budget_min": 100000,
            "budget_max": 200000,
            "city": "Ташкент",
            "preferred_date": "2023-10-10",
            "requirements": ["Опыт 5 лет"]
        }
        '''
        mock_model.generate_content.return_value = mock_response
        
        # Patch sys.modules to include google.generativeai
        with patch.dict('sys.modules', {'google': MagicMock(), 'google.generativeai': mock_genai}):
            # We also need to patch GEMINI_AVAILABLE in the service module
            # But since it's already imported, we need to patch it on the module object
            with patch('marketplace.services.ai_service.GEMINI_AVAILABLE', True):
                # And we need to ensure the service uses our mock model, 
                # but the service initializes 'model' at module level if available.
                # Since it wasn't available at import time, 'model' variable might not exist or be None.
                # We need to patch the 'model' variable in the service module if it exists, 
                # or the _parse_with_gemini method re-imports or uses the global one.
                
                # Let's look at ai_service.py again. 
                # It does: model = genai.GenerativeModel(...) inside the try/except block at module level.
                # So if we patch GEMINI_AVAILABLE, we also need to inject 'model' into the module.
                
                with patch('marketplace.services.ai_service.model', mock_model, create=True):
                    text = "Нужен репетитор"
                    result = AIService._parse_with_gemini(text)
                    
                    self.assertEqual(result['title'], "Репетитор по математике")
                    self.assertEqual(result['city'], "Ташкент")
                    self.assertEqual(result['budget_min'], 100000)
