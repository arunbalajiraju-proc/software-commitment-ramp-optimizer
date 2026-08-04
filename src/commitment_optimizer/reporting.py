"""Create machine-readable and human-readable simulation reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import SimulationSummary
from .optimizer import OptimizationResult


def summary_rows(summaries: list[SimulationSummary]) -> list[dict[str, float | str]]:
    return [
        {
            "option": item.option_name,
            "expected_total_cost": round(item.expected_total_cost, 2),
            "median_total_cost": round(item.median_total_cost, 2),
            "p90_total_cost": round(item.p90_total_cost, 2),
            "cvar_total_cost": round(item.cvar_total_cost, 2),
            "risk_adjusted_cost": round(item.risk_adjusted_cost, 2),
            "expected_unused_cost": round(item.expected_unused_cost, 2),
            "expected_overage_cost": round(item.expected_overage_cost, 2),
            "expected_unused_unit_months": round(item.expected_unused_unit_months, 2),
            "expected_overage_unit_months": round(item.expected_overage_unit_months, 2),
            "expected_utilization_pct": round(item.expected_utilization_pct, 2),
            "expected_overage_share_pct": round(
                100 * item.expected_overage_unit_months / max(sum(item.monthly_expected_demand), 1),
                2,
            ),
        }
        for item in summaries
    ]


def write_report_bundle(
    output_directory: str | Path,
    summaries: list[SimulationSummary],
    optimized: OptimizationResult | None = None,
    break_even_premium: float | None = None,
) -> None:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    rows = summary_rows(summaries)

    with (output / "option_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    detail = {
        "commercial_options": [item.to_dict() for item in summaries],
        "optimized_policy": (
            {
                "option": optimized.option.to_dict(),
                "summary": optimized.summary.to_dict(),
                "candidates_evaluated": optimized.candidates_evaluated,
                "candidates_feasible": optimized.candidates_feasible,
            }
            if optimized
            else None
        ),
        "break_even_flexibility_premium_pct": (
            round(break_even_premium * 100, 4) if break_even_premium is not None else None
        ),
    }
    with (output / "analysis.json").open("w", encoding="utf-8") as handle:
        json.dump(detail, handle, indent=2)

    lines = [
        "# Simulation results",
        "",
        "> These results are model outputs under documented assumptions. "
        "They are not realized savings.",
        "",
        "| Rank | Commercial option | Expected cost | P90 cost | Risk-adjusted cost | "
        "Unused cost | Overage share |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for index, item in enumerate(summaries, start=1):
        overage_share = (
            100 * item.expected_overage_unit_months / max(sum(item.monthly_expected_demand), 1)
        )
        lines.append(
            f"| {index} | {item.option_name} | ${item.expected_total_cost:,.0f} | "
            f"${item.p90_total_cost:,.0f} | ${item.risk_adjusted_cost:,.0f} | "
            f"${item.expected_unused_cost:,.0f} | "
            f"{overage_share:.1f}% |"
        )
    if optimized:
        lines.extend(
            [
                "",
                "## Optimized negotiation scenario",
                "",
                f"- Policy: {optimized.option.name}",
                f"- Candidates evaluated: {optimized.candidates_evaluated}",
                f"- Candidates meeting the overage guardrail: {optimized.candidates_feasible}",
                f"- Expected cost: ${optimized.summary.expected_total_cost:,.0f}",
                f"- P90 cost: ${optimized.summary.p90_total_cost:,.0f}",
                f"- Risk-adjusted cost: ${optimized.summary.risk_adjusted_cost:,.0f}",
            ]
        )
        if break_even_premium is not None:
            lines.append(
                "- Modelled break-even unit-price premium over the public cost "
                f"proxy: {break_even_premium:.1%}"
            )
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def monthly_rows(summaries: list[SimulationSummary]) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    for item in summaries:
        for index, (demand, commitment, cost) in enumerate(
            zip(
                item.monthly_expected_demand,
                item.monthly_expected_commitment,
                item.monthly_expected_cost,
                strict=True,
            ),
            start=1,
        ):
            rows.append(
                {
                    "option": item.option_name,
                    "month": index,
                    "expected_demand": round(demand, 2),
                    "expected_commitment": round(commitment, 2),
                    "expected_monthly_cost": round(cost, 2),
                }
            )
    return rows


def write_monthly_csv(output_directory: str | Path, summaries: list[SimulationSummary]) -> None:
    output = Path(output_directory)
    rows = monthly_rows(summaries)
    with (output / "monthly_profile.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
