from decimal import Decimal
from .models import TariffRule

class PricingEngine:
    @staticmethod
    def calculate_price(
        category_id, 
        district_id, 
        tariff_type, 
        budget: Decimal, 
        responses_count: int, 
        specialist_level: str
    ) -> Decimal:
        """
        Pure function to calculate price or commission amount.
        """
        # 1. Find Rule (Specific District > Default District)
        rule = TariffRule.objects.filter(
            category_id=category_id, 
            tariff_type=tariff_type,
            district_id=district_id
        ).first()
        
        if not rule:
            # Fallback to no-district specific rule
            rule = TariffRule.objects.filter(
                category_id=category_id, 
                tariff_type=tariff_type,
                district_id__isnull=True
            ).first()
        
        if not rule:
            # Fallback default if absolutely no rule exists
            return Decimal('5000') # MVP safety net

        price = rule.base_price

        # 2. Budget Multiplier
        budget_multiplier = Decimal('1.0')
        sorted_tiers = sorted(rule.budget_tiers, key=lambda x: x['max_budget'] or float('inf'))
        for tier in sorted_tiers:
            limit = tier.get('max_budget')
            if limit is None or budget <= Decimal(str(limit)):
                budget_multiplier = Decimal(str(tier.get('multiplier', 1.0)))
                break
        
        price *= budget_multiplier

        # 3. Competition Multiplier
        # config: {"base": 1.0, "step": 0.05, "max_cap": 1.5}
        comp_cfg = rule.competition_config or {}
        comp_base = Decimal(str(comp_cfg.get('base', 1.0)))
        step = Decimal(str(comp_cfg.get('step', 0.0)))
        max_cap = Decimal(str(comp_cfg.get('max_cap', 1.0)))
        
        added_val = min(Decimal(responses_count) * step, max_cap - comp_base)
        comp_multiplier = comp_base + added_val
        price *= comp_multiplier

        # 4. Level Multiplier
        # Hardcoded for MVP or fetch from settings
        LEVEL_COEFFS = {
            'NEW': Decimal('1.0'),
            'VERIFIED': Decimal('0.95'),
            'PRO': Decimal('0.9'),
            'TOP': Decimal('0.85'),
        }
        level_multi = LEVEL_COEFFS.get(specialist_level, Decimal('1.0'))
        price *= level_multi

        # 5. Min/Max Constraints
        price = max(rule.min_price, min(price, rule.max_price))

        return price.quantize(Decimal('1'))
