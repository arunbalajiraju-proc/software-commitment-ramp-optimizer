"""Evaluation of actual supplier offers against a common demand scenario set."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO

from .forecast import generate_demand_scenarios
from .models import CommercialOption, PriceTier, SimulationSummary
from .planner import PlannerResult, recommended_start_units
from .simulation import simulate_option


@dataclass(frozen=True)
class SupplierQuote:
    """Commercial fields needed to compare a supplier's licence offer."""

    offer_name: str
    unit_price_month: float
    initial_commitment_units: int
    adjustment_frequency_months: int
    allow_true_down: bool
    minimum_commitment_units: int
    buffer_pct: float = 0.0
    overage_premium_pct: float = 0.10
    annual_escalation_pct: float = 0.0
    one_time_fee: float = 0.0
    monthly_fixed_fee: float = 0.0

    def __post_init__(self) -> None:
        if not self.offer_name.strip():
            raise ValueError("offer_name cannot be blank")
        if self.unit_price_month <= 0:
            raise ValueError("unit_price_month must be positive")
        if self.initial_commitment_units < 0:
            raise ValueError("initial_commitment_units cannot be negative")
        if self.minimum_commitment_units < 0:
            raise ValueError("minimum_commitment_units cannot be negative")
        if self.initial_commitment_units < self.minimum_commitment_units:
            raise ValueError("initial commitment cannot be below the contractual minimum")
        if self.adjustment_frequency_months < 1:
            raise ValueError("adjustment_frequency_months must be at least 1")
        if (
            min(
                self.buffer_pct,
                self.overage_premium_pct,
                self.annual_escalation_pct,
                self.one_time_fee,
                self.monthly_fixed_fee,
            )
            < 0
        ):
            raise ValueError("quote percentages and fees cannot be negative")


@dataclass(frozen=True)
class SupplierQuoteEvaluation:
    quote: SupplierQuote
    summary: SimulationSummary
    expected_difference_vs_full_commitment: float
    p90_difference_vs_full_commitment: float
    risk_adjusted_difference_vs_full_commitment: float


def quote_to_option(quote: SupplierQuote, target_units: int) -> CommercialOption:
    if target_units < 1:
        raise ValueError("target_units must be at least 1")
    if quote.initial_commitment_units > 2 * target_units:
        raise ValueError("initial commitment cannot exceed twice the planning target")
    return CommercialOption(
        name=quote.offer_name,
        price_tiers=(PriceTier(0, quote.unit_price_month),),
        initial_commitment_pct=quote.initial_commitment_units / target_units,
        adjustment_frequency_months=quote.adjustment_frequency_months,
        allow_true_down=quote.allow_true_down,
        minimum_commitment_units=quote.minimum_commitment_units,
        buffer_pct=quote.buffer_pct,
        overage_multiplier=1.0 + quote.overage_premium_pct,
        one_time_fee=quote.one_time_fee,
        monthly_fixed_fee=quote.monthly_fixed_fee,
        annual_escalation_pct=quote.annual_escalation_pct,
        description="Supplier-entered commercial offer.",
        evidence_class="supplier_quote",
    )


def evaluate_supplier_quotes(
    result: PlannerResult,
    quotes: list[SupplierQuote] | tuple[SupplierQuote, ...],
) -> list[SupplierQuoteEvaluation]:
    """Rank compliant offers using the same seeded scenarios and risk posture."""

    if not quotes:
        raise ValueError("at least one supplier quote is required")
    scenarios = generate_demand_scenarios(result.forecast)
    baseline = result.baseline_summary
    evaluations: list[SupplierQuoteEvaluation] = []
    for quote in quotes:
        option = quote_to_option(quote, result.inputs.target_units)
        summary = simulate_option(
            scenarios,
            option,
            result.inputs.target_units,
            risk_aversion=result.risk_aversion,
            cvar_confidence=result.cvar_confidence,
        )
        evaluations.append(
            SupplierQuoteEvaluation(
                quote=quote,
                summary=summary,
                expected_difference_vs_full_commitment=(
                    baseline.expected_total_cost - summary.expected_total_cost
                ),
                p90_difference_vs_full_commitment=(
                    baseline.p90_total_cost - summary.p90_total_cost
                ),
                risk_adjusted_difference_vs_full_commitment=(
                    baseline.risk_adjusted_cost - summary.risk_adjusted_cost
                ),
            )
        )
    return sorted(evaluations, key=lambda item: item.summary.risk_adjusted_cost)


def supplier_pricing_request_rows(result: PlannerResult) -> list[dict[str, object]]:
    """Create three comparable commercial structures for a sourcing event."""

    option = result.optimized.option
    start_units = recommended_start_units(result)
    target = result.inputs.target_units
    return [
        {
            "pricing_structure": "A - Full upfront commitment",
            "initial_units": target,
            "review_frequency_months": result.inputs.contract_months,
            "true_down_required": False,
            "minimum_units": target,
            "buffer_pct": 0,
            "supplier_unit_price": "",
            "overage_uplift_pct": "",
            "annual_escalation_pct": "",
            "one_time_fees": "",
            "notes": "Control offer for like-for-like TCO comparison.",
        },
        {
            "pricing_structure": "B - Recommended phased activation",
            "initial_units": start_units,
            "review_frequency_months": option.adjustment_frequency_months,
            "true_down_required": option.allow_true_down,
            "minimum_units": option.minimum_commitment_units,
            "buffer_pct": round(option.buffer_pct * 100, 2),
            "supplier_unit_price": "",
            "overage_uplift_pct": "",
            "annual_escalation_pct": "",
            "one_time_fees": "",
            "notes": "Bill additions from activation date; no retroactive repricing.",
        },
        {
            "pricing_structure": "C - Phased activation with true-down",
            "initial_units": start_units,
            "review_frequency_months": option.adjustment_frequency_months,
            "true_down_required": True,
            "minimum_units": result.inputs.day_one_units,
            "buffer_pct": round(option.buffer_pct * 100, 2),
            "supplier_unit_price": "",
            "overage_uplift_pct": "",
            "annual_escalation_pct": "",
            "one_time_fees": "",
            "notes": "Allow reductions at review dates to the agreed committed floor.",
        },
    ]


def supplier_pricing_request_csv(result: PlannerResult) -> str:
    rows = supplier_pricing_request_rows(result)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
