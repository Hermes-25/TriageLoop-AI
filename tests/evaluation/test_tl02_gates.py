import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class TL02GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((ROOT / "artifacts" / "evaluation" / "tl-02-metrics.json").read_text(encoding="utf-8"))
        cls.selected = cls.results["candidates"][cls.results["selection"]["selected"]]

    def test_selected_model_is_gate_qualified_challenger(self) -> None:
        self.assertEqual(self.results["selection"]["selected"], "boosted")
        self.assertTrue(self.results["selection"]["safety_gate_pass"]["boosted"])
        self.assertFalse(self.results["selection"]["safety_gate_pass"]["logistic"])

    def test_recall_and_calibration_gates(self) -> None:
        for horizon in ("5", "15", "30", "60"):
            with self.subTest(horizon=horizon):
                self.assertGreaterEqual(self.selected["test"][horizon]["recall"], 0.90)
                self.assertGreaterEqual(self.selected["stress"][horizon]["recall"], 0.85)
                self.assertLessEqual(self.selected["test"][horizon]["ece"], 0.08)

    def test_critical_conformal_coverage_gate(self) -> None:
        for split in ("test", "stress"):
            for horizon in ("5", "15", "30", "60"):
                with self.subTest(split=split, horizon=horizon):
                    self.assertGreaterEqual(self.selected["conformal"][split][horizon]["critical"], 0.87)

    def test_required_subgroups_are_reported(self) -> None:
        groups = self.selected["subgroups_30m"]["test"]
        self.assertTrue({"age_group:pediatric", "age_group:adult", "age_group:geriatric"}.issubset(groups))
        self.assertTrue({"history_status:none", "history_status:partial", "history_status:available"}.issubset(groups))


if __name__ == "__main__":
    unittest.main()
