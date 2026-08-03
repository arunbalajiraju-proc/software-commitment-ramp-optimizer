import unittest

from commitment_optimizer.planner import (
    PlannerInputs,
    build_planner_configuration,
    procurement_plan_markdown,
    procurement_schedule,
    recommended_start_units,
    run_procurement_plan,
)


class PlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = PlannerInputs(
            deal_name="Test procurement",
            currency="CAD",
            target_units=1_000,
            day_one_units=100,
            unit_price_month=20.0,
            contract_months=24,
            rollout_complete_month=12,
            rollout_confidence="Medium",
            risk_posture="Balanced",
            simulations=30,
            seed=11,
        )

    def test_plain_language_inputs_build_valid_configuration(self) -> None:
        forecast, baseline, template, optimization = build_planner_configuration(
            self.inputs
        )
        self.assertEqual(forecast.rollout_complete_month, 12)
        self.assertEqual(baseline.minimum_commitment_units, 1_000)
        self.assertEqual(template.minimum_commitment_units, 100)
        self.assertIn(0.1, optimization.initial_commitment_pct_grid)

    def test_plan_returns_actionable_schedule_and_memo(self) -> None:
        result = run_procurement_plan(self.inputs)
        start_units = recommended_start_units(result)
        self.assertGreaterEqual(start_units, 100)
        self.assertLessEqual(start_units, 1_000)

        schedule = procurement_schedule(result)
        self.assertEqual(schedule[0]["timing"], "Contract start")
        self.assertEqual(schedule[0]["planned_committed_units"], start_units)
        self.assertTrue(all(row["action"] for row in schedule))

        memo = procurement_plan_markdown(result)
        self.assertIn("Recommended buying approach", memo)
        self.assertIn("Terms to take into the sourcing event", memo)
        self.assertIn("Test procurement", memo)


if __name__ == "__main__":
    unittest.main()
