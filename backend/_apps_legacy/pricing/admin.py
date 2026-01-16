from django.contrib import admin
from .models import TariffRule

@admin.register(TariffRule)
class TariffRuleAdmin(admin.ModelAdmin):
    list_display = ('category', 'district', 'tariff_type', 'base_price')
    list_filter = ('tariff_type', 'category')
