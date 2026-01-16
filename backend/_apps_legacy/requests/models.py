from django.db import models
from django.conf import settings
from apps.catalog.models import Category, District
from django.utils.translation import gettext_lazy as _

class Request(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    district = models.ForeignKey(District, on_delete=models.PROTECT)
    budget = models.DecimalField(max_digits=12, decimal_places=0) # UZS, no cents usually
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.budget}"
