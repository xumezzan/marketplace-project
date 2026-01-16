from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Deal

class FirstPaymentConfirmation(models.Model):
    deal = models.OneToOneField(Deal, on_delete=models.CASCADE, related_name='payment_confirmation')
    code_hash = models.CharField(max_length=128) # Store hashed code
    
    generated_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Confirmation for Deal {self.deal_id}"
