"""Domain models for forecasts, commercial options, and simulation outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, order=True)
class PriceTier:
    """A per-unit monthly price that applies at or above ``minimum_units``."""

    minimum_units: int
    unit_price_month: float

    def __post_init__(self) -> None:
        if self.minimum_units < 0:
            raise ValueError("minimum_units cannot be negative")
        if self.unit_price_month < 0:
            raise ValueError("unit_price_month cannot be negative")


@dataclass(frozen=True)
class ForecastConfig:
    """Parameters used to generate uncertain, non-decreasing adoption paths."""

    horizon_months: int
    target_units: int
    initial_active_units: int
    midpoint_month: float
    growth_rate: float
    rollout_complete_month: int | None = None
    delay_probability: float = 0.0
    delay_min_months: float = 0.0
    delay_mode_months: float = 0.0
    delay_max_months: float = 0.0
    target_volatility_pct: float = 0.0
    growth_volatility_pct: float = 0.0
    simulations: int = 1_000
    seed: int = 42

    def __post_init__(self) -> None:
        if self.horizon_months < 1:
            raise ValueError("horizon_months must be at least 1")
        if self.target_units < 1:
            raise ValueError("target_units must be at least 1")
        if not 0 <= self.initial_active_units <= self.target_units:
            raise ValueError("initial_active_units must be between 0 and target_units")
        if self.growth_rate <= 0:
            raise ValueError("growth_rate must be positive")
        if self.rollout_complete_month is not None and not (
            1 <= self.rollout_complete_month <= self.horizon_months
        ):
            raise ValueError(
                "rollout_complete_month must be between 1 and horizon_months"
            )
        if (
            self.rollout_complete_month == 1
            and self.initial_active_units < self.target_units
        ):
            raise ValueError(
                "rollout_complete_month must be at least 2 when rollout is incomplete"
            )
        if not 0 <= self.delay_probability <= 1:
            raise ValueError("delay_probability must be between 0 and 1")
        if not (
            0 <= self.delay_min_months
            <= self.delay_mode_months
            <= self.delay_max_months
        ):
            raise ValueError("delay values must satisfy 0 <= min <= mode <= max")
        if self.target_volatility_pct < 0 or self.growth_volatility_pct < 0:
            raise ValueError("volatility values cannot be negative")
        if self.simulations < 1:
            raise ValueError("simulations must be at least 1")


@dataclass(frozen=True)
class CommercialOption:
    """A quoted or hypothetical software-commitment policy.

    ``initial_commitment_pct`` and ``buffer_pct`` are proportions, so ``0.25``
    means 25%. Price tiers are evaluated against the committed quantity.
    """

    name: str
    price_tiers: tuple[PriceTier, ...]
    initial_commitment_pct: float
    adjustment_frequency_months: int
    allow_true_down: bool
    minimum_commitment_units: int = 0
    buffer_pct: float = 0.0
    overage_multiplier: float = 1.0
    one_time_fee: float = 0.0
    monthly_fixed_fee: float = 0.0
    annual_escalation_pct: float = 0.0
    unit_price_multiplier: float = 1.0
    description: str = ""
    evidence_class: str = "illustrative"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be blank")
        if not self.price_tiers:
            raise ValueError("at least one price tier is required")
        if tuple(sorted(self.price_tiers)) != self.price_tiers:
            raise ValueError("price_tiers must be sorted by minimum_units")
        if self.price_tiers[0].minimum_units != 0:
            raise ValueError("the first price tier must start at 0 units")
        if not 0 <= self.initial_commitment_pct <= 2:
            raise ValueError("initial_commitment_pct must be between 0 and 2")
        if self.adjustment_frequency_months < 1:
            raise ValueError("adjustment_frequency_months must be at least 1")
        if self.minimum_commitment_units < 0:
            raise ValueError("minimum_commitment_units cannot be negative")
        if self.buffer_pct < 0:
            raise ValueError("buffer_pct cannot be negative")
        if self.overage_multiplier < 1:
            raise ValueError("overage_multiplier must be at least 1")
        if min(
            self.one_time_fee,
            self.monthly_fixed_fee,
            self.annual_escalation_pct,
            self.unit_price_multiplier,
        ) < 0:
            raise ValueError("fees, escalation, and multipliers cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["price_tiers"] = [asdict(tier) for tier in self.price_tiers]
        return data


@dataclass(frozen=True)
class OptimizationConfig:
    """Search space and objective settings for a proposed negotiated policy."""

    initial_commitment_pct_grid: tuple[float, ...] = (
        0.05,
        0.075,
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
        0.65,
        0.80,
        1.00,
    )
    buffer_pct_grid: tuple[float, ...] = (0.0, 0.05, 0.10, 0.20)
    adjustment_frequency_options: tuple[int, ...] = (1, 3, 6, 12)
    allow_true_down_options: tuple[bool, ...] = (False, True)
    frequency_premium_pct: dict[int, float] = field(
        default_factory=lambda: {1: 0.20, 3: 0.12, 6: 0.06, 12: 0.0}
    )
    true_down_premium_pct: float = 0.08
    risk_aversion: float = 0.25
    cvar_confidence: float = 0.90
    max_expected_overage_share: float | None = 0.10

    def __post_init__(self) -> None:
        if not self.initial_commitment_pct_grid:
            raise ValueError("initial commitment grid cannot be empty")
        if not self.adjustment_frequency_options:
            raise ValueError("adjustment frequency options cannot be empty")
        if any(value < 0 for value in self.initial_commitment_pct_grid):
            raise ValueError("initial commitment percentages cannot be negative")
        if any(value < 0 for value in self.buffer_pct_grid):
            raise ValueError("buffer percentages cannot be negative")
        if any(value < 1 for value in self.adjustment_frequency_options):
            raise ValueError("adjustment frequencies must be at least 1")
        if self.true_down_premium_pct < 0 or self.risk_aversion < 0:
            raise ValueError("premiums and risk aversion cannot be negative")
        if not 0 < self.cvar_confidence < 1:
            raise ValueError("cvar_confidence must be between 0 and 1")
        if self.max_expected_overage_share is not None and not (
            0 <= self.max_expected_overage_share <= 1
        ):
            raise ValueError("max_expected_overage_share must be between 0 and 1")


@dataclass(frozen=True)
class SimulationSummary:
    """Aggregated stochastic result for one commercial option."""

    option_name: str
    expected_total_cost: float
    median_total_cost: float
    p90_total_cost: float
    cvar_total_cost: float
    expected_unused_cost: float
    expected_overage_cost: float
    expected_unused_unit_months: float
    expected_overage_unit_months: float
    expected_utilization_pct: float
    risk_adjusted_cost: float
    monthly_expected_demand: tuple[float, ...]
    monthly_expected_commitment: tuple[float, ...]
    monthly_expected_cost: tuple[float, ...]
    total_cost_samples: tuple[float, ...] = field(repr=False)

    def to_dict(self, include_samples: bool = False) -> dict[str, Any]:
        data = asdict(self)
        if not include_samples:
            data.pop("total_cost_samples", None)
        return data
