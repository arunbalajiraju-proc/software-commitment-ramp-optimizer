"""Command-line interface for reproducible case-study runs."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .analysis import find_break_even_premium
from .case_loader import load_case
from .forecast import generate_demand_scenarios
from .optimizer import optimize_policy
from .reporting import write_monthly_csv, write_report_bundle
from .simulation import compare_options


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate software commitment and ramp strategies."
    )
    parser.add_argument("--case", required=True, help="Path to a case-study JSON file")
    parser.add_argument("--output", required=True, help="Directory for generated results")
    parser.add_argument(
        "--skip-optimization",
        action="store_true",
        help="Evaluate the quoted options without searching a negotiation policy",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    case = load_case(args.case)
    scenarios = generate_demand_scenarios(case.forecast)
    summaries = compare_options(
        scenarios,
        case.commercial_options,
        case.forecast.target_units,
        risk_aversion=case.optimization.risk_aversion,
        cvar_confidence=case.optimization.cvar_confidence,
    )
    optimized = None
    break_even_premium = None
    if not args.skip_optimization:
        optimized = optimize_policy(
            scenarios,
            case.optimization_template,
            case.forecast.target_units,
            case.optimization,
        )
        combined = summaries + [optimized.summary]
        summaries = sorted(combined, key=lambda item: item.risk_adjusted_cost)
        unpriced_flexibility = replace(
            optimized.option,
            unit_price_multiplier=case.optimization_template.unit_price_multiplier,
        )
        break_even_premium = find_break_even_premium(
            scenarios,
            case.commercial_options[0],
            unpriced_flexibility,
            case.forecast.target_units,
            risk_aversion=case.optimization.risk_aversion,
            cvar_confidence=case.optimization.cvar_confidence,
        )

    output = Path(args.output)
    write_report_bundle(output, summaries, optimized, break_even_premium)
    write_monthly_csv(output, summaries)
    print(f"Wrote analysis to {output.resolve()}")


if __name__ == "__main__":
    main()
