import unittest

import numpy as np

from commitment_optimizer.forecast import (
    deterministic_adoption_curve,
    generate_demand_scenarios,
)
from commitment_optimizer.models import ForecastConfig


class ForecastTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ForecastConfig(
            horizon_months=24,
            target_units=10_000,
            initial_active_units=500,
            midpoint_month=10,
            growth_rate=0.4,
            delay_probability=0.5,
            delay_min_months=1,
            delay_mode_months=3,
            delay_max_months=6,
            target_volatility_pct=0.1,
            growth_volatility_pct=0.1,
            simulations=100,
            seed=7,
        )

    def test_deterministic_curve_is_bounded_and_non_decreasing(self) -> None:
        curve = deterministic_adoption_curve(self.config)
        self.assertEqual(curve[0], 500)
        self.assertEqual(curve[-1], 10_000)
        self.assertTrue(np.all(np.diff(curve) >= 0))

    def test_scenarios_are_reproducible(self) -> None:
        first = generate_demand_scenarios(self.config)
        second = generate_demand_scenarios(self.config)
        np.testing.assert_array_equal(first, second)
        self.assertEqual(first.shape, (100, 24))
        self.assertTrue(np.all(np.diff(first, axis=1) >= 0))

    def test_guided_rollout_reaches_target_and_then_holds(self) -> None:
        guided = ForecastConfig(
            horizon_months=24,
            target_units=1_000,
            initial_active_units=100,
            midpoint_month=5.5,
            growth_rate=0.5,
            rollout_complete_month=12,
            simulations=1,
        )
        curve = deterministic_adoption_curve(guided)
        self.assertEqual(curve[0], 100)
        self.assertEqual(curve[11], 1_000)
        np.testing.assert_array_equal(curve[11:], np.full(13, 1_000))


if __name__ == "__main__":
    unittest.main()
