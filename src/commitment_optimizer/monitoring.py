"""Post-award licence reconciliation and commitment-control calculations."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class UsageSnapshot:
    """One auditable usage review at a contract checkpoint."""

    committed_units: int
    active_units: int
    assigned_but_inactive_units: int
    unit_price_month: float
    buffer_pct: float = 0.10
    true_down_allowed: bool = False

    def __post_init__(self) -> None:
        if (
            min(
                self.committed_units,
                self.active_units,
                self.assigned_but_inactive_units,
            )
            < 0
        ):
            raise ValueError("usage quantities cannot be negative")
        if self.unit_price_month <= 0:
            raise ValueError("unit_price_month must be positive")
        if self.buffer_pct < 0:
            raise ValueError("buffer_pct cannot be negative")
        if self.assigned_but_inactive_units > self.committed_units:
            raise ValueError("inactive assigned units cannot exceed committed units")


@dataclass(frozen=True)
class UsageReviewResult:
    status: str
    utilization_pct: float
    unused_units: int
    current_unused_cost_month: float
    annualized_unused_cost_exposure: float
    reclaim_now_units: int
    recommended_commitment_units: int
    commitment_change_units: int
    primary_action: str
    follow_up_actions: tuple[str, ...]


def review_usage(snapshot: UsageSnapshot) -> UsageReviewResult:
    """Turn usage evidence into a contract action without assuming true-down rights."""

    unused_units = max(snapshot.committed_units - snapshot.active_units, 0)
    current_unused_cost = unused_units * snapshot.unit_price_month
    recommended_commitment = ceil(snapshot.active_units * (1.0 + snapshot.buffer_pct))
    commitment_change = recommended_commitment - snapshot.committed_units
    reclaim_now = min(snapshot.assigned_but_inactive_units, unused_units)

    if snapshot.committed_units == 0:
        utilization = 100.0 if snapshot.active_units == 0 else 0.0
    else:
        utilization = 100.0 * snapshot.active_units / snapshot.committed_units

    if commitment_change < 0 and snapshot.true_down_allowed:
        status = "Reduce at the next contractual review"
        primary_action = (
            f"Submit a true-down for {abs(commitment_change):,} units and reset the "
            f"commitment to {recommended_commitment:,}."
        )
    elif commitment_change < 0:
        status = "Stop net-new purchases and use the existing pool"
        primary_action = (
            f"The contract does not permit true-down. Avoid the next "
            f"{abs(commitment_change):,} net-new units, reassign the pool, and seek a "
            "credit or renewal reduction."
        )
    elif commitment_change > 0:
        status = "Plan a controlled true-up"
        primary_action = (
            f"Validate demand and add no more than {commitment_change:,} units to reach "
            f"usage plus the {snapshot.buffer_pct:.0%} buffer."
        )
    else:
        status = "Commitment is aligned"
        primary_action = "Maintain the current quantity and repeat the usage review next month."

    actions = [
        f"Reclaim or reassign {reclaim_now:,} assigned-but-inactive units now.",
        "Retain the source usage report, reconciliation date, and approver with the PO record.",
        "Check leavers, duplicate assignments, test accounts, and lower-cost licence profiles.",
    ]
    if not snapshot.true_down_allowed and unused_units:
        actions.append(
            "Open a supplier conversation on credits, delayed billing, swaps, or renewal relief."
        )

    return UsageReviewResult(
        status=status,
        utilization_pct=utilization,
        unused_units=unused_units,
        current_unused_cost_month=current_unused_cost,
        annualized_unused_cost_exposure=current_unused_cost * 12,
        reclaim_now_units=reclaim_now,
        recommended_commitment_units=recommended_commitment,
        commitment_change_units=commitment_change,
        primary_action=primary_action,
        follow_up_actions=tuple(actions),
    )
