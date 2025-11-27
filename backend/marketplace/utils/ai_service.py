"""
AI Service for generating content using Google Gemini API.
"""
import os
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Configure API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_task_description(title: str, category_name: str) -> str:
    """
    Generates a detailed task description based on title and category.
    
    Args:
        title: Task title (e.g., "Fix leaking tap")
        category_name: Category name (e.g., "Plumbing")
        
    Returns:
        Generated description string or empty string if failed.
    """
    if not GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY not set, skipping AI generation")
        return ""
        
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as a helpful assistant for a service marketplace.
        A user wants to create a task with the title: "{title}" in the category: "{category_name}".
        
        Please generate a professional, detailed description for this task that a specialist would understand.
        Include potential details they might need to know (e.g., tools needed, specific conditions).
        Keep it concise but informative (max 150 words).
        Return ONLY the description text, no markdown formatting or headers.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error generating task description: {str(e)}")
        return ""

def suggest_specialists(task_description: str) -> list:
    """
    Analyzes task description and suggests relevant specialist skills/tags.
    (Placeholder for future implementation)
    """
    return []
