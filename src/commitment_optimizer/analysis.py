"""Decision-support analyses built on the simulation engine."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from .models import CommercialOption
from .simulation import simulate_option


def find_break_even_premium(
    scenarios: np.ndarray,
    locked_option: CommercialOption,
    flexible_option: CommercialOption,
    planning_target_units: int,
    *,
    maximum_premium_pct: float = 2.0,
    tolerance: float = 0.0001,
    risk_aversion: float = 0.25,
    cvar_confidence: float = 0.90,
) -> float | None:
    """Find the maximum flexible-price premium that still beats a locked plan.

    Returns a proportion (``0.18`` means 18%). ``None`` means the flexible
    option is already more expensive at a zero premium.
    """

    locked = simulate_option(
        scenarios,
        locked_option,
        planning_target_units,
        risk_aversion=risk_aversion,
        cvar_confidence=cvar_confidence,
    )

    def flexible_cost(premium: float) -> float:
        candidate = replace(
            flexible_option,
            unit_price_multiplier=flexible_option.unit_price_multiplier * (1.0 + premium),
        )
        return simulate_option(
            scenarios,
            candidate,
            planning_target_units,
            risk_aversion=risk_aversion,
            cvar_confidence=cvar_confidence,
        ).risk_adjusted_cost

    if flexible_cost(0.0) > locked.risk_adjusted_cost:
        return None
    if flexible_cost(maximum_premium_pct) <= locked.risk_adjusted_cost:
        return maximum_premium_pct

    low, high = 0.0, maximum_premium_pct
    while high - low > tolerance:
        midpoint = (low + high) / 2.0
        if flexible_cost(midpoint) <= locked.risk_adjusted_cost:
            low = midpoint
        else:
            high = midpoint
    return low
