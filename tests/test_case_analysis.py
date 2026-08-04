import unittest

from commitment_optimizer.case_analysis import usage_aligned_counterfactual


class CaseAnalysisTests(unittest.TestCase):
    def test_toronto_retrospective_is_reconciled_and_labelled(self) -> None:
        result = usage_aligned_counterfactual(
            examined_spend=8_996_400,
            reported_unused_cost=6_896_597,
            flexibility_premium_pct=0.15,
        )
        self.assertEqual(result.used_cost_proxy, 2_099_803)
        self.assertAlmostEqual(result.phased_cost_proxy, 2_414_773.45)
        self.assertAlmostEqual(result.modelled_difference, 6_581_626.55)
        self.assertGreater(result.break_even_premium_pct, 3.0)


if __name__ == "__main__":
    unittest.main()
