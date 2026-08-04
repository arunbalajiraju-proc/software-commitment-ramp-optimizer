import unittest

from commitment_optimizer.planner import PlannerInputs, run_procurement_plan
from commitment_optimizer.quotes import (
    SupplierQuote,
    evaluate_supplier_quotes,
    supplier_pricing_request_rows,
)


class SupplierQuoteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_procurement_plan(
            PlannerInputs(
                deal_name="Quote comparison",
                currency="CAD",
                target_units=1_000,
                day_one_units=100,
                unit_price_month=20.0,
                contract_months=24,
                rollout_complete_month=18,
                simulations=30,
                seed=19,
            )
        )

    def test_actual_offers_are_ranked_on_common_scenarios(self) -> None:
        full = SupplierQuote(
            offer_name="Full",
            unit_price_month=20.0,
            initial_commitment_units=1_000,
            adjustment_frequency_months=24,
            allow_true_down=False,
            minimum_commitment_units=1_000,
        )
        phased = SupplierQuote(
            offer_name="Phased",
            unit_price_month=22.0,
            initial_commitment_units=100,
            adjustment_frequency_months=3,
            allow_true_down=True,
            minimum_commitment_units=100,
            buffer_pct=0.10,
        )
        evaluations = evaluate_supplier_quotes(self.result, [full, phased])
        self.assertEqual(len(evaluations), 2)
        self.assertEqual(evaluations[0].quote.offer_name, "Phased")
        self.assertGreater(
            evaluations[0].risk_adjusted_difference_vs_full_commitment,
            0,
        )

    def test_supplier_request_contains_comparable_structures(self) -> None:
        rows = supplier_pricing_request_rows(self.result)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["initial_units"], 1_000)
        self.assertTrue(rows[2]["true_down_required"])


if __name__ == "__main__":
    unittest.main()
