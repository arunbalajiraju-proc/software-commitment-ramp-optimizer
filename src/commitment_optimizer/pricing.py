"""Commercial-option pricing and single-path cash-flow calculation."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

import numpy as np

from .models import CommercialOption


@dataclass(frozen=True)
class PathResult:
    total_cost: float
    unused_cost: float
    overage_cost: float
    unused_unit_months: int
    overage_unit_months: int
    utilization_pct: float
    monthly_commitment: np.ndarray
    monthly_cost: np.ndarray


def unit_price(option: CommercialOption, committed_units: int, month: int) -> float:
    """Return the applicable unit price for a commitment and contract month."""

    applicable = option.price_tiers[0]
    for tier in option.price_tiers:
        if committed_units >= tier.minimum_units:
            applicable = tier
        else:
            break
    escalation_factor = (1.0 + option.annual_escalation_pct) ** (month // 12)
    return applicable.unit_price_month * option.unit_price_multiplier * escalation_factor


def simulate_path(
    demand: np.ndarray,
    option: CommercialOption,
    planning_target_units: int,
) -> PathResult:
    """Calculate billed capacity, unused capacity, and overage for one path.

    The buyer can add emergency units between formal adjustment dates, but
    those units incur ``overage_multiplier`` and do not permanently alter the
    committed baseline until the next review date.
    """

    if demand.ndim != 1 or demand.size == 0:
        raise ValueError("demand must be a non-empty one-dimensional array")
    if np.any(demand < 0):
        raise ValueError("demand cannot contain negative values")

    initial_commitment = ceil(planning_target_units * option.initial_commitment_pct)
    commitment = max(option.minimum_commitment_units, initial_commitment)
    monthly_commitment = np.empty(demand.size, dtype=int)
    monthly_cost = np.empty(demand.size, dtype=float)

    total_cost = option.one_time_fee
    unused_cost = 0.0
    overage_cost = 0.0
    unused_unit_months = 0
    overage_unit_months = 0
    total_demand = 0
    total_billed_units = 0

    for month, active_units_raw in enumerate(demand):
        active_units = int(active_units_raw)
        if month > 0 and month % option.adjustment_frequency_months == 0:
            requested = ceil(active_units * (1.0 + option.buffer_pct))
            if option.allow_true_down:
                commitment = max(option.minimum_commitment_units, requested)
            else:
                commitment = max(commitment, option.minimum_commitment_units, requested)

        base_price = unit_price(option, commitment, month)
        overage_units = max(active_units - commitment, 0)
        unused_units = max(commitment - active_units, 0)

        base_cost = commitment * base_price
        current_overage_cost = overage_units * base_price * option.overage_multiplier
        current_cost = base_cost + current_overage_cost + option.monthly_fixed_fee

        monthly_commitment[month] = commitment
        monthly_cost[month] = current_cost
        total_cost += current_cost
        unused_cost += unused_units * base_price
        overage_cost += current_overage_cost
        unused_unit_months += unused_units
        overage_unit_months += overage_units
        total_demand += active_units
        total_billed_units += commitment + overage_units

    utilization_pct = (
        100.0 if total_billed_units == 0 else 100.0 * total_demand / total_billed_units
    )
    return PathResult(
        total_cost=total_cost,
        unused_cost=unused_cost,
        overage_cost=overage_cost,
        unused_unit_months=unused_unit_months,
        overage_unit_months=overage_unit_months,
        utilization_pct=utilization_pct,
        monthly_commitment=monthly_commitment,
        monthly_cost=monthly_cost,
    )
