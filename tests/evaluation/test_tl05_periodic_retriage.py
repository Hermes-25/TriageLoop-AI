import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class TL05PeriodicRetriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = ROOT / "artifacts" / "evaluation" / "tl-05-periodic-retriage-metrics.json"
        if not cls.path.exists():
            raise unittest.SkipTest("run TL-05 periodic re-triage experiment first")
        cls.results = json.loads(cls.path.read_text(encoding="utf-8"))

    def test_stronger_comparator_is_explicit_and_complete(self) -> None:
        self.assertEqual(self.results["policies"], ["static_periodic", "triageloop"])
        self.assertEqual(self.results["periodic_retriage_minutes"], 15)
        self.assertEqual(self.results["total_policy_shifts"], 1200)
        self.assertTrue(self.results["interpretation_gates"]["all_cells_have_registered_replications"])

    def test_no_retroactive_twenty_percent_gate_is_claimed(self) -> None:
        self.assertIn("not this stronger TL-05 comparator", self.results["registered_gate_notice"])

    def test_all_site_load_cells_report_paired_miss_results(self) -> None:
        for site in ("community", "regional", "urban_trauma"):
            for load in ("baseline", "surge_3x"):
                result = self.results["paired_comparisons"][f"{site}|{load}|action_window_miss_rate"]
                self.assertIn("relative_improvement", result)
                self.assertIn("ci95_low", result)
                self.assertIn("ci95_high", result)

    def test_periodic_comparator_response_sensitivity_is_explicit(self) -> None:
        sensitivity = self.results["deterioration_response_sensitivity"]
        self.assertEqual(set(sensitivity), {"10", "20", "30"})
        for result in sensitivity.values():
            self.assertIn("periodic_retriage_mean", result)
            self.assertIn("triageloop_mean", result)
            self.assertIn("relative_improvement", result)
            self.assertEqual(result["paired_policy_shifts"], 180)
        self.assertIn("post-verification", self.results["sensitivity_notice"])


if __name__ == "__main__":
    unittest.main()
