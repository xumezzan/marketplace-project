import pytest
from decimal import Decimal
from apps.pricing.services import PricingEngine
from apps.pricing.models import TariffRule
from apps.catalog.models import Category, District

@pytest.fixture
def setup_pricing_data(db):
    cat = Category.objects.create(name='Plumber')
    rule = TariffRule.objects.create(
        category=cat,
        tariff_type='RESPONSE',
        base_price=Decimal('10000'),
        min_price=Decimal('5000'),
        max_price=Decimal('50000'),
        budget_tiers=[
            {"max_budget": 100000, "multiplier": 1.0},
            {"max_budget": 500000, "multiplier": 1.5},
            {"max_budget": None, "multiplier": 2.0}
        ],
        competition_config={"base": 1.0, "step": 0.1, "max_cap": 1.5}
    )
    return cat, rule

@pytest.mark.django_db
class TestPricingEngine:
    def test_basic_calculation(self, setup_pricing_data):
        cat, _ = setup_pricing_data
        price = PricingEngine.calculate_price(
            category_id=cat.id,
            district_id=None,
            tariff_type='RESPONSE',
            budget=Decimal('50000'),
            responses_count=0,
            specialist_level='NEW'
        )
        # Base 10000 * Budget 1.0 * Comp 1.0 * Level 1.0 = 10000
        assert price == Decimal('10000')

    def test_budget_tier_multiplier(self, setup_pricing_data):
        cat, _ = setup_pricing_data
        price = PricingEngine.calculate_price(
            category_id=cat.id, 
            district_id=None, 
            tariff_type='RESPONSE',
            budget=Decimal('200000'), # Fits in 500000 tier (1.5)
            responses_count=0, 
            specialist_level='NEW'
        )
        # 10000 * 1.5 = 15000
        assert price == Decimal('15000')

    def test_competition_multiplier(self, setup_pricing_data):
        cat, _ = setup_pricing_data
        price = PricingEngine.calculate_price(
            category_id=cat.id, 
            district_id=None, 
            tariff_type='RESPONSE',
            budget=Decimal('50000'),
            responses_count=3, # 3 * 0.1 = 0.3 added. Total 1.3
            specialist_level='NEW'
        )
        # 10000 * 1.3 = 13000
        assert price == Decimal('13000')

    def test_specialist_discount(self, setup_pricing_data):
        cat, _ = setup_pricing_data
        price = PricingEngine.calculate_price(
            category_id=cat.id,
            district_id=None,
            tariff_type='RESPONSE',
            budget=Decimal('50000'),
            responses_count=0,
            specialist_level='TOP' # 0.85
        )
        # 10000 * 0.85 = 8500
        assert price == Decimal('8500')

    def test_max_price_cap(self, setup_pricing_data):
        cat, rule = setup_pricing_data
        rule.base_price = Decimal('100000') # High base
        rule.save()
        
        price = PricingEngine.calculate_price(
            category_id=cat.id,
            district_id=None,
            tariff_type='RESPONSE',
            budget=Decimal('1000000'), # Multiplier 2.0
            responses_count=0,
            specialist_level='NEW'
        )
        # Calc: 100000 * 2.0 = 200000. But Max is 50000
        assert price == Decimal('50000')
