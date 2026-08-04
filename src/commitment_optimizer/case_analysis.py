"""Strictly labelled retrospective calculations for public case studies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrospectiveCounterfactual:
    examined_spend: float
    reported_unused_cost: float
    used_cost_proxy: float
    flexibility_premium_pct: float
    phased_cost_proxy: float
    modelled_difference: float
    break_even_premium_pct: float


def usage_aligned_counterfactual(
    examined_spend: float,
    reported_unused_cost: float,
    flexibility_premium_pct: float,
) -> RetrospectiveCounterfactual:
    """Estimate an upper-bound difference if billing followed observed use.

    This is intentionally retrospective. It does not claim the observed usage path,
    price, or contractual flexibility was known or obtainable before signature.
    """

    if examined_spend <= 0:
        raise ValueError("examined_spend must be positive")
    if not 0 <= reported_unused_cost <= examined_spend:
        raise ValueError("reported_unused_cost must fall within examined_spend")
    if flexibility_premium_pct < 0:
        raise ValueError("flexibility_premium_pct cannot be negative")

    used_cost = examined_spend - reported_unused_cost
    phased_cost = used_cost * (1.0 + flexibility_premium_pct)
    difference = examined_spend - phased_cost
    break_even = reported_unused_cost / used_cost if used_cost else float("inf")
    return RetrospectiveCounterfactual(
        examined_spend=examined_spend,
        reported_unused_cost=reported_unused_cost,
        used_cost_proxy=used_cost,
        flexibility_premium_pct=flexibility_premium_pct,
        phased_cost_proxy=phased_cost,
        modelled_difference=difference,
        break_even_premium_pct=break_even,
    )
