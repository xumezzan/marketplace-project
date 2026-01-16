from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    class TariffType(models.TextChoices):
        COMMISSION = 'COMMISSION', _('Commission')
        RESPONSE = 'RESPONSE', _('Response')

    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    default_tariff = models.CharField(max_length=20, choices=TariffType.choices, default=TariffType.RESPONSE)
    icon = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=255, unique=True)
    city = models.CharField(max_length=255, default='Tashkent')
    
    def __str__(self):
        return f"{self.name}, {self.city}"
