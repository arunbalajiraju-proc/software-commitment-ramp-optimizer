"""Buyer-facing translation layer for guided software procurement planning."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from math import ceil
from typing import Any

from .analysis import find_break_even_premium
from .forecast import generate_demand_scenarios
from .models import (
    CommercialOption,
    ForecastConfig,
    OptimizationConfig,
    PriceTier,
    SimulationSummary,
)
from .optimizer import OptimizationResult, optimize_policy
from .readiness import ReadinessAssessment, ReadinessInputs, assess_readiness
from .simulation import simulate_option

DEFAULT_FREQUENCY_PREMIUMS = {1: 0.20, 3: 0.12, 6: 0.06, 12: 0.0}

_CONFIDENCE_ASSUMPTIONS: dict[str, dict[str, float]] = {
    "High": {
        "delay_probability": 0.20,
        "delay_min_months": 1.0,
        "delay_mode_months": 2.0,
        "delay_max_months": 4.0,
        "target_volatility_pct": 0.05,
        "growth_volatility_pct": 0.08,
    },
    "Medium": {
        "delay_probability": 0.40,
        "delay_min_months": 1.0,
        "delay_mode_months": 3.0,
        "delay_max_months": 6.0,
        "target_volatility_pct": 0.10,
        "growth_volatility_pct": 0.15,
    },
    "Low": {
        "delay_probability": 0.65,
        "delay_min_months": 2.0,
        "delay_mode_months": 6.0,
        "delay_max_months": 12.0,
        "target_volatility_pct": 0.20,
        "growth_volatility_pct": 0.25,
    },
}

_RISK_SETTINGS: dict[str, tuple[float, float]] = {
    "Cost focused": (0.10, 0.15),
    "Balanced": (0.25, 0.10),
    "Conservative": (0.50, 0.05),
}


@dataclass(frozen=True)
class PlannerInputs:
    """Plain-language facts a sourcing or delivery team can reasonably provide."""

    deal_name: str
    currency: str
    target_units: int
    day_one_units: int
    unit_price_month: float
    contract_months: int
    rollout_complete_month: int
    unit_label: str = "licence units"
    rollout_confidence: str = "Medium"
    risk_posture: str = "Balanced"
    overage_premium_pct: float = 0.10
    frequency_premium_pct: dict[int, float] = field(
        default_factory=lambda: dict(DEFAULT_FREQUENCY_PREMIUMS)
    )
    true_down_premium_pct: float = 0.08
    simulations: int = 500
    seed: int = 20260803
    readiness: ReadinessInputs = field(default_factory=ReadinessInputs)

    def __post_init__(self) -> None:
        if not self.deal_name.strip():
            raise ValueError("deal_name cannot be blank")
        if not self.currency.strip():
            raise ValueError("currency cannot be blank")
        if not self.unit_label.strip():
            raise ValueError("unit_label cannot be blank")
        if self.target_units < 1:
            raise ValueError("target_units must be at least 1")
        if not 0 <= self.day_one_units <= self.target_units:
            raise ValueError("day_one_units must be between 0 and target_units")
        if self.unit_price_month <= 0:
            raise ValueError("unit_price_month must be positive")
        if self.contract_months < 2:
            raise ValueError("contract_months must be at least 2")
        if not 2 <= self.rollout_complete_month <= self.contract_months:
            raise ValueError("rollout_complete_month must be between 2 and contract_months")
        if self.rollout_confidence not in _CONFIDENCE_ASSUMPTIONS:
            raise ValueError("rollout_confidence must be High, Medium, or Low")
        if self.risk_posture not in _RISK_SETTINGS:
            raise ValueError("risk_posture must be Cost focused, Balanced, or Conservative")
        if self.overage_premium_pct < 0 or self.true_down_premium_pct < 0:
            raise ValueError("commercial premiums cannot be negative")
        if any(month < 1 or premium < 0 for month, premium in self.frequency_premium_pct.items()):
            raise ValueError("review frequencies and premiums must be positive")
        if self.simulations < 1:
            raise ValueError("simulations must be at least 1")


@dataclass(frozen=True)
class PlannerResult:
    """Procurement decision and the model artefacts supporting it."""

    inputs: PlannerInputs
    forecast: ForecastConfig
    baseline_option: CommercialOption
    baseline_summary: SimulationSummary
    optimized: OptimizationResult
    break_even_premium: float | None
    readiness_assessment: ReadinessAssessment
    risk_aversion: float
    cvar_confidence: float


def _growth_rate(rollout_complete_month: int) -> float:
    """Translate an intuitive completion month into a usable S-curve slope."""

    rollout_span = max(rollout_complete_month - 1, 4)
    return min(0.80, max(0.15, 6.0 / rollout_span))


def _initial_commitment_grid(inputs: PlannerInputs) -> tuple[float, ...]:
    floor_pct = inputs.day_one_units / inputs.target_units
    standard = (0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.65, 0.80, 1.00)
    candidates = {round(floor_pct, 6), 1.0}
    candidates.update(value for value in standard if value >= floor_pct)
    return tuple(sorted(candidates))


def build_planner_configuration(
    inputs: PlannerInputs,
) -> tuple[ForecastConfig, CommercialOption, CommercialOption, OptimizationConfig]:
    """Convert buyer-facing answers into forecast and commercial model objects."""

    uncertainty = _CONFIDENCE_ASSUMPTIONS[inputs.rollout_confidence]
    risk_aversion, max_overage_share = _RISK_SETTINGS[inputs.risk_posture]
    completion_index = inputs.rollout_complete_month - 1
    forecast = ForecastConfig(
        horizon_months=inputs.contract_months,
        target_units=inputs.target_units,
        initial_active_units=inputs.day_one_units,
        midpoint_month=max(1.0, completion_index / 2.0),
        growth_rate=_growth_rate(inputs.rollout_complete_month),
        rollout_complete_month=inputs.rollout_complete_month,
        simulations=inputs.simulations,
        seed=inputs.seed,
        **uncertainty,
    )
    overage_multiplier = 1.0 + inputs.overage_premium_pct
    price_tiers = (PriceTier(0, inputs.unit_price_month),)
    baseline = CommercialOption(
        name="Commit all planned licences at contract start",
        price_tiers=price_tiers,
        initial_commitment_pct=1.0,
        adjustment_frequency_months=inputs.contract_months,
        allow_true_down=False,
        minimum_commitment_units=inputs.target_units,
        overage_multiplier=overage_multiplier,
        description="Buyer commits the full planned quantity when the contract starts.",
        evidence_class="user_entered_baseline",
    )
    template = CommercialOption(
        name="Phased commitment template",
        price_tiers=price_tiers,
        initial_commitment_pct=inputs.day_one_units / inputs.target_units,
        adjustment_frequency_months=6,
        allow_true_down=False,
        minimum_commitment_units=inputs.day_one_units,
        overage_multiplier=overage_multiplier,
        description="Negotiable phased activation structure generated from user inputs.",
        evidence_class="modelled_negotiation_template",
    )
    optimization = OptimizationConfig(
        initial_commitment_pct_grid=_initial_commitment_grid(inputs),
        buffer_pct_grid=(0.0, 0.05, 0.10, 0.20),
        adjustment_frequency_options=(1, 3, 6, 12),
        allow_true_down_options=(False, True),
        frequency_premium_pct=dict(inputs.frequency_premium_pct),
        true_down_premium_pct=inputs.true_down_premium_pct,
        risk_aversion=risk_aversion,
        cvar_confidence=0.90,
        max_expected_overage_share=max_overage_share,
    )
    return forecast, baseline, template, optimization


def run_procurement_plan(inputs: PlannerInputs) -> PlannerResult:
    """Run the risk-adjusted engine from a compact set of procurement inputs."""

    forecast, baseline, template, optimization = build_planner_configuration(inputs)
    scenarios = generate_demand_scenarios(forecast)
    baseline_summary = simulate_option(
        scenarios,
        baseline,
        inputs.target_units,
        risk_aversion=optimization.risk_aversion,
        cvar_confidence=optimization.cvar_confidence,
    )
    optimized = optimize_policy(
        scenarios,
        template,
        inputs.target_units,
        optimization,
    )
    unpriced_flexibility = replace(optimized.option, unit_price_multiplier=1.0)
    break_even = find_break_even_premium(
        scenarios,
        baseline,
        unpriced_flexibility,
        inputs.target_units,
        risk_aversion=optimization.risk_aversion,
        cvar_confidence=optimization.cvar_confidence,
    )
    return PlannerResult(
        inputs=inputs,
        forecast=forecast,
        baseline_option=baseline,
        baseline_summary=baseline_summary,
        optimized=optimized,
        break_even_premium=break_even,
        readiness_assessment=assess_readiness(inputs.readiness),
        risk_aversion=optimization.risk_aversion,
        cvar_confidence=optimization.cvar_confidence,
    )


def review_frequency_label(months: int) -> str:
    labels = {1: "monthly", 3: "every 3 months", 6: "every 6 months", 12: "annually"}
    return labels.get(months, f"every {months} months")


def recommended_start_units(result: PlannerResult) -> int:
    option = result.optimized.option
    return max(
        option.minimum_commitment_units,
        ceil(result.inputs.target_units * option.initial_commitment_pct),
    )


def procurement_schedule(result: PlannerResult) -> list[dict[str, Any]]:
    """Build an expected review schedule from the selected dynamic policy."""

    option = result.optimized.option
    summary = result.optimized.summary
    indices = [
        0,
        *range(
            option.adjustment_frequency_months,
            result.inputs.contract_months,
            option.adjustment_frequency_months,
        ),
    ]
    rows: list[dict[str, Any]] = []
    previous_commitment = 0
    for index in indices:
        commitment = ceil(summary.monthly_expected_commitment[index])
        expected_active = ceil(summary.monthly_expected_demand[index])
        change = commitment - previous_commitment
        if index == 0:
            action = f"Place initial order for {commitment:,}"
        elif change > 0:
            action = f"Plan to add up to {change:,} after the usage review"
        elif change < 0:
            action = f"Reduce by about {abs(change):,} if true-down is exercised"
        else:
            action = "No additional order forecast; complete the usage review"
        rows.append(
            {
                "contract_month": index + 1,
                "timing": "Contract start" if index == 0 else f"After month {index}",
                "expected_active_units": expected_active,
                "planned_committed_units": commitment,
                "planned_change_units": change,
                "action": action,
            }
        )
        previous_commitment = commitment
    return rows


def _money(currency: str, value: float) -> str:
    return f"{currency} {value:,.0f}"


def procurement_plan_markdown(result: PlannerResult) -> str:
    """Create a portable sourcing recommendation for download or review."""

    inputs = result.inputs
    option = result.optimized.option
    summary = result.optimized.summary
    start_units = recommended_start_units(result)
    difference = result.baseline_summary.risk_adjusted_cost - summary.risk_adjusted_cost
    premium = (
        "No positive premium identified"
        if result.break_even_premium is None
        else f"{result.break_even_premium:.1%} above the full-commitment unit price"
    )
    true_down = "Include true-down rights" if option.allow_true_down else "Use true-up only"
    readiness = result.readiness_assessment
    schedule = procurement_schedule(result)
    lines = [
        f"# Procurement plan: {inputs.deal_name}",
        "",
        "> Planning guidance generated from user-entered assumptions. Validate quantities, "
        "supplier terms, implementation dependencies, and legal language before award.",
        "",
        "## Approval gate",
        "",
        f"- Decision: **{readiness.decision}**.",
        f"- Modelled quantity: **{start_units:,} {inputs.unit_label}**. This is not an "
        "approved PO quantity until the readiness conditions below are closed.",
    ]
    if readiness.blockers:
        lines.extend(["- Full-commitment blockers:"])
        lines.extend(f"  - {item}" for item in readiness.blockers)
    if readiness.conditions:
        lines.extend(["- Commercial and operating conditions:"])
        lines.extend(f"  - {item}" for item in readiness.conditions)
    if readiness.record_gaps:
        lines.extend(["- Decision-record gaps:"])
        lines.extend(f"  - {item}" for item in readiness.record_gaps)
    lines.extend(
        [
            "",
            "## Recommended buying approach",
            "",
            f"- Start with **{start_units:,} {inputs.unit_label}** "
            f"({start_units / inputs.target_units:.1%} of the "
            f"{inputs.target_units:,} planned need).",
            "- Review actual active usage "
            f"**{review_frequency_label(option.adjustment_frequency_months)}**.",
            "- At each review, set the commitment to active usage plus a "
            f"**{option.buffer_pct:.0%} buffer**.",
            f"- {true_down}.",
            f"- Pricing guardrail for phased flexibility: **{premium}**.",
            "",
            "## Expected procurement schedule",
            "",
            "| Timing | Expected active | Planned commitment | Change | Action |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for row in schedule:
        lines.append(
            f"| {row['timing']} | {row['expected_active_units']:,} | "
            f"{row['planned_committed_units']:,} | {row['planned_change_units']:+,} | "
            f"{row['action']} |"
        )
    lines.extend(
        [
            "",
            "## Modelled financial comparison",
            "",
            f"- Full upfront commitment, risk-adjusted cost: "
            f"**{_money(inputs.currency, result.baseline_summary.risk_adjusted_cost)}**",
            f"- Recommended phased plan, risk-adjusted cost: "
            f"**{_money(inputs.currency, summary.risk_adjusted_cost)}**",
            f"- Modelled difference: **{_money(inputs.currency, difference)}**",
            f"- Recommended plan P90 budget: **{_money(inputs.currency, summary.p90_total_cost)}**",
            "",
            "## Terms to take into the sourcing event",
            "",
            f"1. Initial order or committed floor of {start_units:,} {inputs.unit_label}.",
            "2. Formal quantity review "
            f"{review_frequency_label(option.adjustment_frequency_months)}.",
            f"3. Commitment reset to measured active usage plus {option.buffer_pct:.0%}.",
            f"4. {true_down}; prohibit retroactive overage repricing.",
            f"5. Cap emergency overage at {inputs.overage_premium_pct:.0%} above "
            "the contracted unit price.",
            "6. Invoice new quantities only from their activation date.",
            "7. Preserve licence reassignment and transfer rights where the metric permits.",
            "8. Require usage reporting before every scheduled quantity review.",
            "",
            "## Before award",
            "",
            "- Reconcile the eligible population with HR, identity, device, or "
            "application records.",
            "- Confirm rollout milestones and dependencies with the implementation owner.",
            "- Obtain comparable pricing for full commitment and phased activation.",
            "- Replace assumed flexibility premiums with supplier quotes and rerun the plan.",
            "- Put the agreed activation schedule and adjustment mechanics in the order form.",
            "- Record Procurement, Finance, Project, IT/Architecture, Security/Privacy, "
            "and Legal approvals or documented exceptions before issuing the PO.",
        ]
    )
    return "\n".join(lines) + "\n"
