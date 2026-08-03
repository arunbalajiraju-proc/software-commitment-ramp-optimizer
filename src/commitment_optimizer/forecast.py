"""Demand and deployment scenario generation."""

from __future__ import annotations

import numpy as np

from .models import ForecastConfig


def deterministic_adoption_curve(
    config: ForecastConfig,
    *,
    target_units: float | None = None,
    midpoint_month: float | None = None,
    growth_rate: float | None = None,
) -> np.ndarray:
    """Create a smooth, non-decreasing logistic adoption path.

    The curve is normalized so month zero equals ``initial_active_units`` and
    the final month reaches the scenario target. This is a planning model, not
    an assertion about how a particular organization deployed software.
    """

    target = float(config.target_units if target_units is None else target_units)
    target = max(float(config.initial_active_units), target)
    midpoint = config.midpoint_month if midpoint_month is None else midpoint_month
    rate = config.growth_rate if growth_rate is None else growth_rate

    months = np.arange(config.horizon_months, dtype=float)
    raw = 1.0 / (1.0 + np.exp(-rate * (months - midpoint)))
    raw_start = raw[0]
    raw_end = raw[-1]
    if np.isclose(raw_start, raw_end):
        normalized = np.linspace(0.0, 1.0, config.horizon_months)
    else:
        normalized = np.clip((raw - raw_start) / (raw_end - raw_start), 0.0, 1.0)

    curve = config.initial_active_units + (
        target - config.initial_active_units
    ) * normalized
    curve = np.maximum.accumulate(np.rint(curve)).astype(int)
    return curve


def generate_demand_scenarios(config: ForecastConfig) -> np.ndarray:
    """Generate reproducible uncertain adoption paths.

    Each scenario varies the ultimate demand, adoption speed, and—when the
    Bernoulli delay event occurs—the midpoint of the rollout. Delays use a
    triangular distribution because sourcing teams can often provide a
    minimum, most-likely, and maximum delay even when little history exists.
    """

    rng = np.random.default_rng(config.seed)
    scenarios = np.empty((config.simulations, config.horizon_months), dtype=int)

    target_sigma = config.target_volatility_pct
    growth_sigma = config.growth_volatility_pct

    for index in range(config.simulations):
        target_multiplier = max(0.05, rng.normal(1.0, target_sigma))
        scenario_target = max(
            config.initial_active_units,
            int(round(config.target_units * target_multiplier)),
        )
        growth_multiplier = max(0.10, rng.normal(1.0, growth_sigma))
        scenario_growth = config.growth_rate * growth_multiplier

        delay = 0.0
        if (
            config.delay_probability > 0
            and rng.random() < config.delay_probability
            and config.delay_max_months > 0
        ):
            delay = float(
                rng.triangular(
                    config.delay_min_months,
                    config.delay_mode_months,
                    config.delay_max_months,
                )
            )

        scenarios[index] = deterministic_adoption_curve(
            config,
            target_units=scenario_target,
            midpoint_month=config.midpoint_month + delay,
            growth_rate=scenario_growth,
        )

    return scenarios
