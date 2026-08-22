import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class TL03GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((ROOT / "artifacts" / "evaluation" / "tl-03-queue-metrics.json").read_text(encoding="utf-8"))

    def test_full_registered_matrix_ran(self) -> None:
        self.assertEqual(self.results["total_policy_shifts"], 1800)
        self.assertEqual(set(self.results["site_profiles"]), {"community", "regional", "urban_trauma"})
        self.assertTrue(self.results["gates"]["all_cells_have_100_replications"])

    def test_overall_surge_miss_reduction_gate(self) -> None:
        comparison = self.results["overall_surge"]["action_window_miss_rate"]
        self.assertGreaterEqual(comparison["relative_improvement"], 0.20)
        self.assertGreater(comparison["ci95_low"], 0)

    def test_each_site_point_estimate_improves_by_twenty_percent(self) -> None:
        for site in self.results["site_profiles"]:
            with self.subTest(site=site):
                comparison = self.results["paired_comparisons"][f"{site}|surge_3x|action_window_miss_rate"]
                self.assertGreaterEqual(comparison["relative_improvement"], 0.20)

    def test_low_acuity_tail_guardrail(self) -> None:
        comparison = self.results["overall_surge"]["low_acuity_p90_wait_minutes"]
        self.assertLessEqual(comparison["triageloop_mean"], 1.20 * comparison["static_mean"])

    def test_negative_slack_and_signal_delay_improve(self) -> None:
        self.assertGreater(self.results["overall_surge"]["negative_slack_minutes"]["relative_improvement"], 0)
        self.assertGreater(self.results["overall_surge"]["mean_signal_to_action_minutes"]["relative_improvement"], 0)

    def test_consolidated_alert_workload_is_reported_per_nurse_hour(self) -> None:
        workload = self.results["alert_workload"]
        self.assertEqual(set(workload), {"community", "regional", "urban_trauma"})
        for site in workload.values():
            self.assertEqual(set(site), {"baseline", "surge_3x"})
            for cell in site.values():
                self.assertGreater(cell["reassessment_nurses"], 0)
                self.assertGreaterEqual(cell["mean_consolidated_alerts_per_8h_shift"], 0)
                self.assertGreaterEqual(cell["mean_alerts_per_reassessment_nurse_hour"], 0)

    def test_community_surge_workload_warning_remains_visible_in_evidence(self) -> None:
        community = self.results["alert_workload"]["community"]["surge_3x"]
        self.assertGreater(community["mean_alerts_per_reassessment_nurse_hour"], 5.0)


if __name__ == "__main__":
    unittest.main()
