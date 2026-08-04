import unittest

from commitment_optimizer.readiness import (
    CONFIRMED,
    HOLD_FULL_COMMITMENT,
    PHASE_WITH_CONDITIONS,
    READY_FOR_COMMERCIAL_DECISION,
    ReadinessInputs,
    assess_readiness,
)


class ReadinessTests(unittest.TestCase):
    def test_unassessed_evidence_holds_full_commitment(self) -> None:
        assessment = assess_readiness(ReadinessInputs())
        self.assertEqual(assessment.decision, HOLD_FULL_COMMITMENT)
        self.assertFalse(assessment.full_commitment_allowed)
        self.assertGreaterEqual(len(assessment.blockers), 4)

    def test_confirmed_evidence_with_missing_controls_requires_phasing(self) -> None:
        assessment = assess_readiness(
            ReadinessInputs(
                demand_evidence_status=CONFIRMED,
                technical_capacity_status=CONFIRMED,
                implementation_plan_status=CONFIRMED,
                critical_dependencies_status=CONFIRMED,
                usage_reporting_status=CONFIRMED,
            )
        )
        self.assertEqual(assessment.decision, PHASE_WITH_CONDITIONS)
        self.assertTrue(assessment.conditions)

    def test_complete_control_record_is_ready_for_commercial_decision(self) -> None:
        assessment = assess_readiness(
            ReadinessInputs(
                demand_evidence_status=CONFIRMED,
                technical_capacity_status=CONFIRMED,
                implementation_plan_status=CONFIRMED,
                critical_dependencies_status=CONFIRMED,
                usage_reporting_status=CONFIRMED,
                phased_pricing_requested=True,
                usage_review_owner="SAM lead",
            )
        )
        self.assertEqual(assessment.decision, READY_FOR_COMMERCIAL_DECISION)
        self.assertTrue(assessment.full_commitment_allowed)


if __name__ == "__main__":
    unittest.main()
