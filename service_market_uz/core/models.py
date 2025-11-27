from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class AIRequest(models.Model):
    """
    Log of AI requests.
    """
    class RequestType(models.TextChoices):
        PARSE = 'parse', _('Parse Text')
        ESTIMATE = 'estimate', _('Estimate Price')
        
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_requests'
    )
    request_type = models.CharField(max_length=20, choices=RequestType.choices)
    input_data = models.JSONField()
    output_data = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.request_type} ({self.created_at})"
