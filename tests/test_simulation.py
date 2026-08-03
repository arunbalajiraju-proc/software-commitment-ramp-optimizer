import unittest

import numpy as np

from commitment_optimizer.models import CommercialOption, PriceTier
from commitment_optimizer.simulation import compare_options, simulate_option


class SimulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios = np.array(
            [
                [10, 20, 30, 40, 50, 60],
                [10, 15, 20, 25, 30, 35],
            ]
        )
        self.locked = CommercialOption(
            name="Locked",
            price_tiers=(PriceTier(0, 1.0),),
            initial_commitment_pct=1.0,
            adjustment_frequency_months=12,
            allow_true_down=False,
            minimum_commitment_units=60,
        )
        self.flexible = CommercialOption(
            name="Flexible",
            price_tiers=(PriceTier(0, 1.1),),
            initial_commitment_pct=0.2,
            adjustment_frequency_months=1,
            allow_true_down=True,
            overage_multiplier=1.05,
        )

    def test_summary_has_expected_dimensions(self) -> None:
        summary = simulate_option(self.scenarios, self.locked, 60)
        self.assertEqual(len(summary.monthly_expected_cost), 6)
        self.assertEqual(len(summary.total_cost_samples), 2)
        self.assertGreater(summary.expected_unused_cost, 0)

    def test_comparison_ranks_lower_risk_adjusted_cost_first(self) -> None:
        ranked = compare_options(self.scenarios, [self.locked, self.flexible], 60)
        self.assertEqual(ranked[0].option_name, "Flexible")


if __name__ == "__main__":
    unittest.main()
