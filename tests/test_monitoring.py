import unittest

from commitment_optimizer.monitoring import UsageSnapshot, review_usage


class MonitoringTests(unittest.TestCase):
    def test_true_down_action_quantifies_reduction_and_exposure(self) -> None:
        result = review_usage(
            UsageSnapshot(
                committed_units=1_000,
                active_units=700,
                assigned_but_inactive_units=50,
                unit_price_month=25.0,
                buffer_pct=0.10,
                true_down_allowed=True,
            )
        )
        self.assertEqual(result.unused_units, 300)
        self.assertEqual(result.current_unused_cost_month, 7_500)
        self.assertEqual(result.recommended_commitment_units, 771)
        self.assertEqual(result.commitment_change_units, -229)
        self.assertIn("true-down", result.primary_action)

    def test_no_true_down_freezes_net_new_purchases(self) -> None:
        result = review_usage(
            UsageSnapshot(
                committed_units=1_000,
                active_units=700,
                assigned_but_inactive_units=50,
                unit_price_month=25.0,
                buffer_pct=0.10,
                true_down_allowed=False,
            )
        )
        self.assertIn("Stop net-new purchases", result.status)


if __name__ == "__main__":
    unittest.main()
