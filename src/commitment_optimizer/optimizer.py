"""Transparent search over proposed commitment and adjustment policies."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .models import CommercialOption, OptimizationConfig, SimulationSummary
from .simulation import simulate_option


@dataclass(frozen=True)
class OptimizationResult:
    option: CommercialOption
    summary: SimulationSummary
    candidates_evaluated: int
    candidates_feasible: int


def _percent_label(value: float) -> str:
    percentage = value * 100
    decimals = 0 if percentage.is_integer() else 1
    return f"{percentage:.{decimals}f}%"


def optimize_policy(
    scenarios: np.ndarray,
    base_option: CommercialOption,
    planning_target_units: int,
    config: OptimizationConfig | None = None,
) -> OptimizationResult:
    """Find the best policy in an explicit, auditable candidate grid.

    More frequent adjustments and true-down rights apply user-configured price
    premiums. Those premiums are negotiating assumptions, not market facts.
    """

    search = config or OptimizationConfig()
    best_option: CommercialOption | None = None
    best_summary: SimulationSummary | None = None
    candidates = 0
    feasible = 0

    for initial_pct in search.initial_commitment_pct_grid:
        # Avoid duplicate/mislabelled candidates when an explicit commercial
        # floor is higher than a percentage in the search grid.
        if planning_target_units * initial_pct < base_option.minimum_commitment_units:
            continue
        for buffer_pct in search.buffer_pct_grid:
            for frequency in search.adjustment_frequency_options:
                for allow_true_down in search.allow_true_down_options:
                    frequency_premium = search.frequency_premium_pct.get(frequency, 0.0)
                    true_down_premium = search.true_down_premium_pct if allow_true_down else 0.0
                    multiplier = base_option.unit_price_multiplier * (
                        1.0 + frequency_premium + true_down_premium
                    )
                    candidate = replace(
                        base_option,
                        name=(
                            f"Optimized: {_percent_label(initial_pct)} initial, "
                            f"{frequency}-month review, "
                            f"{'true-down' if allow_true_down else 'true-up only'}, "
                            f"{_percent_label(buffer_pct)} buffer"
                        ),
                        initial_commitment_pct=initial_pct,
                        buffer_pct=buffer_pct,
                        adjustment_frequency_months=frequency,
                        allow_true_down=allow_true_down,
                        unit_price_multiplier=multiplier,
                        evidence_class="modelled_negotiation_scenario",
                    )
                    summary = simulate_option(
                        scenarios,
                        candidate,
                        planning_target_units,
                        risk_aversion=search.risk_aversion,
                        cvar_confidence=search.cvar_confidence,
                    )
                    candidates += 1
                    expected_demand_unit_months = sum(summary.monthly_expected_demand)
                    overage_share = (
                        0.0
                        if expected_demand_unit_months == 0
                        else summary.expected_overage_unit_months / expected_demand_unit_months
                    )
                    if (
                        search.max_expected_overage_share is not None
                        and overage_share > search.max_expected_overage_share
                    ):
                        continue
                    feasible += 1
                    if best_summary is None or (
                        summary.risk_adjusted_cost < best_summary.risk_adjusted_cost
                    ):
                        best_option = candidate
                        best_summary = summary

    if best_option is None or best_summary is None:
        raise RuntimeError(
            "optimizer found no feasible candidates; relax the overage constraint "
            "or expand the search grid"
        )
    return OptimizationResult(best_option, best_summary, candidates, feasible)
