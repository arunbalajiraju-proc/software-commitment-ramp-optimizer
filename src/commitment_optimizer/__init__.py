"""Risk-adjusted software commitment and licence-ramp optimization."""

from .analysis import find_break_even_premium
from .forecast import deterministic_adoption_curve, generate_demand_scenarios
from .models import (
    CommercialOption,
    ForecastConfig,
    OptimizationConfig,
    PriceTier,
    SimulationSummary,
)
from .optimizer import optimize_policy
from .simulation import compare_options, simulate_option

__all__ = [
    "CommercialOption",
    "ForecastConfig",
    "OptimizationConfig",
    "PriceTier",
    "SimulationSummary",
    "compare_options",
    "deterministic_adoption_curve",
    "find_break_even_premium",
    "generate_demand_scenarios",
    "optimize_policy",
    "simulate_option",
]

__version__ = "0.1.0"
