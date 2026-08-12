"""Transparent, illustrative operating-scenario calculations.

All profile inputs are examples, not real-company operating data.  Keeping the
formula here makes every number in the prototype auditable and easy to change.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class MarketProfile:
    currency: str
    baseline_orders: float
    unit_price_local: float
    baseline_fx_cny: float
    unit_cogs_cny: float
    unit_logistics_cny: float
    platform_fee_rate: float
    price_elasticity: float


@dataclass(frozen=True)
class ScenarioInputs:
    """Fractional changes: 0.05 represents a five-percent increase."""
    fx_change: float = 0.0
    logistics_change: float = 0.0
    price_change: float = 0.0
    cogs_change: float = 0.0


@dataclass(frozen=True)
class ScenarioResult:
    orders: float
    unit_price_local: float
    fx_rate_cny: float
    unit_cogs_cny: float
    unit_logistics_cny: float
    revenue_cny: float
    variable_cost: float
    contribution_profit: float
    contribution_margin: float


MARKET_PROFILES: dict[str, MarketProfile] = {
    "US": MarketProfile("USD", 12_000, 45.0, 7.20, 110.0, 52.0, 0.15, 1.4),
    "UK": MarketProfile("GBP", 10_000, 38.0, 9.20, 100.0, 55.0, 0.15, 1.6),
    "Eurozone": MarketProfile("EUR", 11_000, 42.0, 7.80, 105.0, 50.0, 0.15, 1.5),
}


def calculate_scenario(profile: MarketProfile, inputs: ScenarioInputs) -> ScenarioResult:
    """Calculate simplified contribution profit under four adjustable shocks."""
    unit_price_local = profile.unit_price_local * (1 + inputs.price_change)
    fx_rate_cny = profile.baseline_fx_cny * (1 + inputs.fx_change)
    unit_cogs_cny = profile.unit_cogs_cny * (1 + inputs.cogs_change)
    unit_logistics_cny = profile.unit_logistics_cny * (1 + inputs.logistics_change)
    orders = max(0.0, profile.baseline_orders * (1 - profile.price_elasticity * inputs.price_change))
    revenue_cny = orders * unit_price_local * fx_rate_cny
    variable_cost = orders * (unit_cogs_cny + unit_logistics_cny) + revenue_cny * profile.platform_fee_rate
    contribution_profit = revenue_cny - variable_cost
    contribution_margin = contribution_profit / revenue_cny if revenue_cny else 0.0
    return ScenarioResult(orders, unit_price_local, fx_rate_cny, unit_cogs_cny, unit_logistics_cny, revenue_cny, variable_cost, contribution_profit, contribution_margin)


def classify_pressure(current: ScenarioResult, baseline: ScenarioResult) -> tuple[str, str]:
    """Return an intentionally simple, explainable operating-pressure label."""
    profit_change = (current.contribution_profit - baseline.contribution_profit) / baseline.contribution_profit if baseline.contribution_profit else 0.0
    if current.contribution_profit <= 0 or current.contribution_margin < 0.10 or profit_change <= -0.30:
        return "high", "Contribution profit or margin is materially pressured; review pricing, logistics and FX hedging first."
    if current.contribution_margin < 0.18 or profit_change <= -0.15:
        return "medium", "Profit headroom is visibly narrower; run factor sensitivity and cost-breakdown checks."
    return "low", "Illustrative shock remains within the selected guardrails; continue monitoring the key drivers."


def calculate_single_factor_impacts(profile: MarketProfile, inputs: ScenarioInputs) -> pd.DataFrame:
    """Show one-factor-at-a-time effects rather than claiming causal precision."""
    baseline = calculate_scenario(profile, ScenarioInputs())
    factors = {
        "FX": ScenarioInputs(fx_change=inputs.fx_change),
        "Logistics": ScenarioInputs(logistics_change=inputs.logistics_change),
        "Price": ScenarioInputs(price_change=inputs.price_change),
        "COGS": ScenarioInputs(cogs_change=inputs.cogs_change),
    }
    rows = []
    for name, single_input in factors.items():
        impact = calculate_scenario(profile, single_input).contribution_profit - baseline.contribution_profit
        rows.append({"factor": name, "contribution_profit_change_cny": impact, "direction": "improves" if impact > 1 else "pressures" if impact < -1 else "unchanged"})
    return pd.DataFrame(rows)
