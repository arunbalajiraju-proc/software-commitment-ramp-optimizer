import unittest
from pathlib import Path

from commitment_optimizer.case_loader import load_case


class CaseLoaderTests(unittest.TestCase):
    def test_loads_toronto_m365_case(self) -> None:
        path = Path("case_studies/toronto/toronto_m365.json")
        case = load_case(path)
        self.assertEqual(case.slug, "toronto-m365")
        self.assertEqual(case.forecast.target_units, 30_000)
        self.assertEqual(len(case.commercial_options), 3)
        self.assertEqual(case.optimization_template.minimum_commitment_units, 2_250)
        self.assertEqual(case.optimization_template.unit_price_multiplier, 1.0)
        self.assertEqual(case.optimization.frequency_premium_pct[6], 0.06)
        self.assertEqual(case.optimization.max_expected_overage_share, 0.10)
        self.assertEqual(case.counterfactual["reported_unused_cost"], 6_896_597)
        self.assertIn("illustrative", case.simulation_notice.lower())


if __name__ == "__main__":
    unittest.main()
