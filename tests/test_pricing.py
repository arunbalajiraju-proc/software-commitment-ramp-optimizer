import unittest

import numpy as np

from commitment_optimizer.models import CommercialOption, PriceTier
from commitment_optimizer.pricing import simulate_path, unit_price


class PricingTests(unittest.TestCase):
    def test_price_tier_selection(self) -> None:
        option = CommercialOption(
            name="Tier test",
            price_tiers=(PriceTier(0, 20.0), PriceTier(1_000, 15.0)),
            initial_commitment_pct=1.0,
            adjustment_frequency_months=12,
            allow_true_down=False,
        )
        self.assertEqual(unit_price(option, 999, 0), 20.0)
        self.assertEqual(unit_price(option, 1_000, 0), 15.0)

    def test_m365_public_cost_proxy_reconciles_year_one(self) -> None:
        option = CommercialOption(
            name="M365 proxy",
            price_tiers=(PriceTier(0, 14.28),),
            initial_commitment_pct=1.0,
            adjustment_frequency_months=12,
            allow_true_down=False,
            minimum_commitment_units=30_000,
        )
        demand = np.full(12, 2_250)
        result = simulate_path(demand, option, 30_000)
        self.assertAlmostEqual(result.total_cost, 5_140_800.0, places=2)
        self.assertAlmostEqual(result.unused_cost, 4_755_240.0, places=2)
        self.assertAlmostEqual(result.utilization_pct, 7.5, places=2)

    def test_true_down_reduces_commitment_at_review(self) -> None:
        option = CommercialOption(
            name="Flexible",
            price_tiers=(PriceTier(0, 10.0),),
            initial_commitment_pct=1.0,
            adjustment_frequency_months=1,
            allow_true_down=True,
        )
        result = simulate_path(np.array([100, 20, 20]), option, 100)
        np.testing.assert_array_equal(result.monthly_commitment, np.array([100, 20, 20]))


if __name__ == "__main__":
    unittest.main()
