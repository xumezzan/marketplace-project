from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Category, District

class TariffRule(models.Model):
    class TariffType(models.TextChoices):
        COMMISSION = 'COMMISSION', _('Commission')
        RESPONSE = 'RESPONSE', _('Response')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tariff_rules')
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True, help_text="Null means all districts default")
    tariff_type = models.CharField(max_length=20, choices=TariffType.choices)
    
    base_price = models.DecimalField(max_digits=12, decimal_places=0)
    min_price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    max_price = models.DecimalField(max_digits=12, decimal_places=0, default=1000000)
    
    # JSON Configs
    # Format: [{"max_budget": 100000, "multiplier": 1.0}, {"max_budget": null, "multiplier": 2.0}]
    budget_tiers = models.JSONField(default=list, blank=True)
    
    # Format: {"base": 1.0, "step": 0.05, "max_cap": 2.0}
    # logic: multiplier = base + min(responses_count, 10) * step
    competition_config = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('category', 'district', 'tariff_type')

    def __str__(self):
        return f"{self.category.name} ({self.tariff_type}) - base {self.base_price}"
