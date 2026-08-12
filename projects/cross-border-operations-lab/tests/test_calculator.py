"""Unit checks for the transparent scenario-calculation module."""

import unittest

from src.calculator import MarketProfile, ScenarioInputs, calculate_scenario, classify_pressure


PROFILE = MarketProfile(
    currency="USD",
    baseline_orders=12_000,
    unit_price_local=45.0,
    baseline_fx_cny=7.2,
    unit_cogs_cny=110.0,
    unit_logistics_cny=52.0,
    platform_fee_rate=0.15,
    price_elasticity=1.4,
)


class ScenarioCalculatorTests(unittest.TestCase):
    def test_baseline_has_positive_profit_and_margin(self):
        result = calculate_scenario(PROFILE, ScenarioInputs())
        self.assertGreater(result.contribution_profit, 0)
        self.assertGreater(result.contribution_margin, 0)
        self.assertLess(result.contribution_margin, 1)

    def test_currency_depreciation_reduces_cny_revenue(self):
        baseline = calculate_scenario(PROFILE, ScenarioInputs())
        depreciated = calculate_scenario(PROFILE, ScenarioInputs(fx_change=-0.05))
        self.assertLess(depreciated.revenue_cny, baseline.revenue_cny)

    def test_deep_cost_shock_triggers_material_pressure(self):
        baseline = calculate_scenario(PROFILE, ScenarioInputs())
        stressed = calculate_scenario(
            PROFILE, ScenarioInputs(cogs_change=0.40, logistics_change=0.50)
        )
        _, guidance = classify_pressure(stressed, baseline)
        self.assertLess(stressed.contribution_profit, baseline.contribution_profit)
        self.assertTrue(guidance)


if __name__ == "__main__":
    unittest.main()
