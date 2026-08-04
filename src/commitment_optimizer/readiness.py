"""Evidence-based gates for approving a software licence commitment."""

from __future__ import annotations

from dataclasses import dataclass

CONFIRMED = "Confirmed"
IN_PROGRESS = "In progress"
NOT_ASSESSED = "Not assessed"
NOT_APPLICABLE = "Not applicable"

READINESS_STATUS_OPTIONS = (
    NOT_ASSESSED,
    IN_PROGRESS,
    CONFIRMED,
    NOT_APPLICABLE,
)

HOLD_FULL_COMMITMENT = "Hold full commitment"
PHASE_WITH_CONDITIONS = "Proceed only with phased commitment"
READY_FOR_COMMERCIAL_DECISION = "Ready for commercial comparison"


@dataclass(frozen=True)
class ReadinessInputs:
    """Small set of evidence checks required before a large commitment."""

    demand_evidence_status: str = NOT_ASSESSED
    technical_capacity_status: str = NOT_ASSESSED
    implementation_plan_status: str = NOT_ASSESSED
    critical_dependencies_status: str = NOT_ASSESSED
    usage_reporting_status: str = NOT_ASSESSED
    pilot_required: bool = False
    pilot_complete: bool = True
    phased_pricing_requested: bool = False
    decision_owner: str = ""
    project_owner: str = ""
    usage_review_owner: str = ""
    demand_evidence_reference: str = ""

    def __post_init__(self) -> None:
        statuses = (
            self.demand_evidence_status,
            self.technical_capacity_status,
            self.implementation_plan_status,
            self.critical_dependencies_status,
            self.usage_reporting_status,
        )
        if any(status not in READINESS_STATUS_OPTIONS for status in statuses):
            raise ValueError("readiness statuses must use the documented options")
        if not self.pilot_required and not self.pilot_complete:
            raise ValueError("pilot_complete cannot be false when no pilot is required")


@dataclass(frozen=True)
class ReadinessAssessment:
    """Governance outcome that sits above the financial optimization."""

    decision: str
    full_commitment_allowed: bool
    blockers: tuple[str, ...]
    conditions: tuple[str, ...]
    record_gaps: tuple[str, ...]


def _is_confirmed(status: str, *, allow_not_applicable: bool = False) -> bool:
    return status == CONFIRMED or (allow_not_applicable and status == NOT_APPLICABLE)


def assess_readiness(inputs: ReadinessInputs) -> ReadinessAssessment:
    """Apply transparent go/no-go rules without producing a misleading score."""

    blockers: list[str] = []
    conditions: list[str] = []
    record_gaps: list[str] = []

    if not _is_confirmed(inputs.demand_evidence_status):
        blockers.append(
            "Validate the day-one and steady-state quantities against a named system "
            "record or deployment-wave list."
        )
    if not _is_confirmed(inputs.technical_capacity_status):
        blockers.append(
            "Confirm that architecture and technical capacity can support the first "
            "deployment wave."
        )
    if not _is_confirmed(inputs.implementation_plan_status):
        blockers.append(
            "Approve a deployment plan with dated waves, dependencies, and accountable owners."
        )
    if not _is_confirmed(
        inputs.critical_dependencies_status,
        allow_not_applicable=True,
    ):
        blockers.append(
            "Clear the critical security, privacy, integration, data, and change dependencies."
        )
    if inputs.pilot_required and not inputs.pilot_complete:
        blockers.append("Complete and accept the required pilot or proof of concept.")

    if not _is_confirmed(inputs.usage_reporting_status):
        conditions.append(
            "Require monthly usage reporting before award and make it available to the buyer."
        )
    if not inputs.phased_pricing_requested:
        conditions.append(
            "Request comparable full-commitment and phased-activation prices from suppliers."
        )
    if not inputs.usage_review_owner.strip():
        conditions.append("Assign an owner for every post-award licence usage review.")

    if not inputs.decision_owner.strip():
        record_gaps.append("Decision owner is not recorded.")
    if not inputs.project_owner.strip():
        record_gaps.append("Project or rollout owner is not recorded.")
    if not inputs.demand_evidence_reference.strip():
        record_gaps.append("Demand evidence reference is not recorded.")

    if blockers:
        decision = HOLD_FULL_COMMITMENT
        full_commitment_allowed = False
    elif conditions:
        decision = PHASE_WITH_CONDITIONS
        full_commitment_allowed = False
    else:
        decision = READY_FOR_COMMERCIAL_DECISION
        full_commitment_allowed = True

    return ReadinessAssessment(
        decision=decision,
        full_commitment_allowed=full_commitment_allowed,
        blockers=tuple(blockers),
        conditions=tuple(conditions),
        record_gaps=tuple(record_gaps),
    )
