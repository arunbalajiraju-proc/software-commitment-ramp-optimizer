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
from .planner import (
    PlannerInputs,
    PlannerResult,
    procurement_plan_markdown,
    procurement_schedule,
    run_procurement_plan,
)
from .simulation import compare_options, simulate_option

__all__ = [
    "CommercialOption",
    "ForecastConfig",
    "OptimizationConfig",
    "PlannerInputs",
    "PlannerResult",
    "PriceTier",
    "SimulationSummary",
    "compare_options",
    "deterministic_adoption_curve",
    "find_break_even_premium",
    "generate_demand_scenarios",
    "optimize_policy",
    "procurement_plan_markdown",
    "procurement_schedule",
    "run_procurement_plan",
    "simulate_option",
]

__version__ = "0.2.0"
