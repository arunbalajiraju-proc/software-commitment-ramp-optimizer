import unittest

import numpy as np

from commitment_optimizer.analysis import find_break_even_premium
from commitment_optimizer.models import (
    CommercialOption,
    OptimizationConfig,
    PriceTier,
)
from commitment_optimizer.optimizer import optimize_policy


class OptimizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios = np.array(
            [
                [10, 15, 20, 30, 40, 50],
                [10, 10, 15, 20, 25, 30],
            ]
        )
        self.base = CommercialOption(
            name="Base",
            price_tiers=(PriceTier(0, 1.0),),
            initial_commitment_pct=1.0,
            adjustment_frequency_months=12,
            allow_true_down=False,
        )

    def test_optimizer_evaluates_grid_and_improves_slow_ramp(self) -> None:
        config = OptimizationConfig(
            initial_commitment_pct_grid=(0.1, 1.0),
            buffer_pct_grid=(0.0,),
            adjustment_frequency_options=(1, 12),
            allow_true_down_options=(False, True),
            frequency_premium_pct={1: 0.0, 12: 0.0},
            true_down_premium_pct=0.0,
            risk_aversion=0.0,
            max_expected_overage_share=None,
        )
        result = optimize_policy(self.scenarios, self.base, 50, config)
        self.assertEqual(result.candidates_evaluated, 8)
        self.assertEqual(result.candidates_feasible, 8)
        self.assertEqual(result.option.initial_commitment_pct, 0.1)

    def test_break_even_premium_is_positive_for_flexible_plan(self) -> None:
        locked = self.base
        flexible = CommercialOption(
            name="Flexible",
            price_tiers=(PriceTier(0, 1.0),),
            initial_commitment_pct=0.1,
            adjustment_frequency_months=1,
            allow_true_down=True,
        )
        premium = find_break_even_premium(self.scenarios, locked, flexible, 50)
        self.assertIsNotNone(premium)
        self.assertGreater(premium or 0, 0)

    def test_optimizer_applies_overage_feasibility_guardrail(self) -> None:
        config = OptimizationConfig(
            initial_commitment_pct_grid=(0.1, 1.0),
            buffer_pct_grid=(0.0,),
            adjustment_frequency_options=(12,),
            allow_true_down_options=(False,),
            frequency_premium_pct={12: 0.0},
            risk_aversion=0.0,
            max_expected_overage_share=0.0,
        )
        result = optimize_policy(self.scenarios, self.base, 50, config)
        self.assertEqual(result.option.initial_commitment_pct, 1.0)
        self.assertEqual(result.candidates_evaluated, 2)
        self.assertEqual(result.candidates_feasible, 1)


if __name__ == "__main__":
    unittest.main()
