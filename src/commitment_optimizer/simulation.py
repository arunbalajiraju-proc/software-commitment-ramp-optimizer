"""Monte Carlo evaluation of software commercial options."""

from __future__ import annotations

import numpy as np

from .models import CommercialOption, SimulationSummary
from .pricing import simulate_path


def _conditional_value_at_risk(samples: np.ndarray, confidence: float) -> float:
    threshold = float(np.quantile(samples, confidence))
    tail = samples[samples >= threshold]
    return float(np.mean(tail)) if tail.size else threshold


def simulate_option(
    scenarios: np.ndarray,
    option: CommercialOption,
    planning_target_units: int,
    *,
    risk_aversion: float = 0.25,
    cvar_confidence: float = 0.90,
) -> SimulationSummary:
    """Evaluate one commercial policy across all demand scenarios."""

    if scenarios.ndim != 2 or scenarios.shape[0] == 0 or scenarios.shape[1] == 0:
        raise ValueError("scenarios must be a non-empty two-dimensional array")
    if planning_target_units < 1:
        raise ValueError("planning_target_units must be at least 1")
    if risk_aversion < 0:
        raise ValueError("risk_aversion cannot be negative")
    if not 0 < cvar_confidence < 1:
        raise ValueError("cvar_confidence must be between 0 and 1")

    count, months = scenarios.shape
    costs = np.empty(count, dtype=float)
    unused_costs = np.empty(count, dtype=float)
    overage_costs = np.empty(count, dtype=float)
    unused_units = np.empty(count, dtype=float)
    overage_units = np.empty(count, dtype=float)
    utilization = np.empty(count, dtype=float)
    commitments = np.empty((count, months), dtype=float)
    monthly_costs = np.empty((count, months), dtype=float)

    for index, path in enumerate(scenarios):
        result = simulate_path(path, option, planning_target_units)
        costs[index] = result.total_cost
        unused_costs[index] = result.unused_cost
        overage_costs[index] = result.overage_cost
        unused_units[index] = result.unused_unit_months
        overage_units[index] = result.overage_unit_months
        utilization[index] = result.utilization_pct
        commitments[index] = result.monthly_commitment
        monthly_costs[index] = result.monthly_cost

    expected_cost = float(np.mean(costs))
    cvar_cost = _conditional_value_at_risk(costs, cvar_confidence)
    risk_adjusted_cost = expected_cost + risk_aversion * (cvar_cost - expected_cost)

    return SimulationSummary(
        option_name=option.name,
        expected_total_cost=expected_cost,
        median_total_cost=float(np.median(costs)),
        p90_total_cost=float(np.quantile(costs, 0.90)),
        cvar_total_cost=cvar_cost,
        expected_unused_cost=float(np.mean(unused_costs)),
        expected_overage_cost=float(np.mean(overage_costs)),
        expected_unused_unit_months=float(np.mean(unused_units)),
        expected_overage_unit_months=float(np.mean(overage_units)),
        expected_utilization_pct=float(np.mean(utilization)),
        risk_adjusted_cost=risk_adjusted_cost,
        monthly_expected_demand=tuple(float(v) for v in np.mean(scenarios, axis=0)),
        monthly_expected_commitment=tuple(float(v) for v in np.mean(commitments, axis=0)),
        monthly_expected_cost=tuple(float(v) for v in np.mean(monthly_costs, axis=0)),
        total_cost_samples=tuple(float(v) for v in costs),
    )


def compare_options(
    scenarios: np.ndarray,
    options: list[CommercialOption] | tuple[CommercialOption, ...],
    planning_target_units: int,
    *,
    risk_aversion: float = 0.25,
    cvar_confidence: float = 0.90,
) -> list[SimulationSummary]:
    """Evaluate and rank commercial options by risk-adjusted cost."""

    if not options:
        raise ValueError("at least one commercial option is required")
    summaries = [
        simulate_option(
            scenarios,
            option,
            planning_target_units,
            risk_aversion=risk_aversion,
            cvar_confidence=cvar_confidence,
        )
        for option in options
    ]
    return sorted(summaries, key=lambda item: item.risk_adjusted_cost)
