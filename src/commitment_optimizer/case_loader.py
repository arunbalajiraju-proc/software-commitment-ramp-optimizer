"""Load documented case-study configurations from JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import CommercialOption, ForecastConfig, OptimizationConfig, PriceTier


@dataclass(frozen=True)
class CaseStudy:
    slug: str
    title: str
    organization: str
    decision_question: str
    published_facts: tuple[dict[str, Any], ...]
    counterfactual: dict[str, Any]
    simulation_notice: str
    forecast: ForecastConfig
    commercial_options: tuple[CommercialOption, ...]
    optimization_template: CommercialOption
    optimization: OptimizationConfig
    sources: tuple[dict[str, str], ...]


def _option_from_dict(data: dict[str, Any]) -> CommercialOption:
    values = dict(data)
    values["price_tiers"] = tuple(PriceTier(**tier) for tier in values.get("price_tiers", []))
    return CommercialOption(**values)


def _optimization_from_dict(data: dict[str, Any]) -> OptimizationConfig:
    values = dict(data)
    tuple_fields = (
        "initial_commitment_pct_grid",
        "buffer_pct_grid",
        "adjustment_frequency_options",
        "allow_true_down_options",
    )
    for field_name in tuple_fields:
        if field_name in values:
            values[field_name] = tuple(values[field_name])
    if "frequency_premium_pct" in values:
        values["frequency_premium_pct"] = {
            int(key): value for key, value in values["frequency_premium_pct"].items()
        }
    return OptimizationConfig(**values)


def load_case(path: str | Path) -> CaseStudy:
    source_path = Path(path)
    with source_path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    return CaseStudy(
        slug=data["slug"],
        title=data["title"],
        organization=data["organization"],
        decision_question=data["decision_question"],
        published_facts=tuple(data["published_facts"]),
        counterfactual=dict(data.get("counterfactual", {})),
        simulation_notice=data["simulation_notice"],
        forecast=ForecastConfig(**data["simulation"]["forecast"]),
        commercial_options=tuple(
            _option_from_dict(option) for option in data["simulation"]["commercial_options"]
        ),
        optimization_template=_option_from_dict(data["simulation"]["optimization_template"]),
        optimization=_optimization_from_dict(data["simulation"]["optimization"]),
        sources=tuple(data["sources"]),
    )
