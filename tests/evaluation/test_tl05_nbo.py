import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class TL05NBOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = ROOT / "artifacts" / "evaluation" / "tl-05-nbo-metrics.json"
        if not cls.path.exists():
            raise unittest.SkipTest("run TL-05 NBO counterfactual first")
        cls.results = json.loads(cls.path.read_text(encoding="utf-8"))

    def test_registered_nbo_gates_are_reported_without_omission(self) -> None:
        self.assertIn("at_least_25pct_fewer_observations", self.results["gates"])
        self.assertIn("no_material_operational_recall_loss", self.results["gates"])
        self.assertIn("0.02 absolute", self.results["material_recall_loss_definition"])

    def test_evaluation_has_critical_cases_and_subgroups(self) -> None:
        self.assertGreater(self.results["eligible_snapshots"], 0)
        self.assertGreater(self.results["critical_snapshots"], 0)
        for field in ("split", "age_group", "history_status"):
            self.assertTrue(self.results["subgroups"][field])

    def test_nbo_never_claims_more_than_one_observation(self) -> None:
        self.assertEqual(self.results["next_best_observation"]["observations_per_reassessment"], 1)
        self.assertEqual(self.results["fixed_bundle"]["observations_per_reassessment"], 8)

    def test_failed_single_observation_gate_is_retained_when_fallback_is_evaluated(self) -> None:
        self.assertFalse(self.results["gates"]["no_material_operational_recall_loss"])
        self.assertIn(self.results["adaptive_bundle_fallback"]["status"], {"qualified", "not_qualified"})
        self.assertEqual(set(self.results["fallback_sensitivity"]), {"1", "2", "3", "4", "5", "6"})
        self.assertEqual(self.results["release_decision"]["status"], "failed_safety_gate")
        self.assertIn("full reassessment", self.results["release_decision"]["safe_fallback"])


if __name__ == "__main__":
    unittest.main()
