from datetime import datetime
import json
from pathlib import Path
import unittest

from triageloop.recommendation import ModelBundle, RecommendedAction, recommend
from triageloop.schemas import PatientState


ROOT = Path(__file__).resolve().parents[2]


class RecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = ModelBundle.from_path(ROOT / "artifacts" / "models" / "tl-02" / "selected-model.json")
        cls.cases = {case["scenario_id"]: case for case in json.loads((ROOT / "data" / "fixtures" / "curated-cases.json").read_text(encoding="utf-8"))}

    def result(self, scenario: str):
        case = self.cases[scenario]
        return recommend(PatientState.model_validate(case["patient"]), self.bundle, evaluated_at=datetime.fromisoformat(case["evaluated_at"]))

    def test_horizon_risk_is_monotone(self) -> None:
        result = self.result("worsening-respiration")
        values = [result.risk_by_horizon[str(horizon)] for horizon in (5, 15, 30, 60)]
        self.assertEqual(values, sorted(values))

    def test_hard_rule_wins_and_window_is_immediate(self) -> None:
        result = self.result("silent-hypoxia")
        self.assertEqual(result.recommended_action, RecommendedAction.IMMEDIATE_REVIEW)
        self.assertEqual(result.action_window.maximum_minutes, 0)
        self.assertIn("HARD_RED_FLAG", result.safety.rule_hits)
        self.assertFalse(result.safety.autonomous_downgrade_permitted)

    def test_missing_critical_observation_enters_safe_mode_and_requests_it(self) -> None:
        result = self.result("missing-spo2")
        self.assertEqual(result.recommended_action, RecommendedAction.SAFE_MODE_REVIEW)
        self.assertTrue(result.safety.safe_mode)
        self.assertEqual(result.next_best_observation.observation_code, "repeat_spo2")

    def test_stable_case_keeps_bounded_monitored_wait(self) -> None:
        result = self.result("stable-low-acuity")
        self.assertEqual(result.recommended_action, RecommendedAction.CONTINUE_MONITORED_WAIT)
        self.assertFalse(result.safety.safe_mode)
        self.assertLessEqual(result.action_window.maximum_minutes, 120)

    def test_worsening_case_is_not_downgraded(self) -> None:
        result = self.result("worsening-respiration")
        self.assertIn(result.recommended_action, {RecommendedAction.ESCALATE_PRIORITY, RecommendedAction.IMMEDIATE_REVIEW, RecommendedAction.SAFE_MODE_REVIEW})
        self.assertFalse(result.safety.autonomous_downgrade_permitted)

    def test_implausible_measurement_requests_targeted_repeat(self) -> None:
        self.assertEqual(self.result("inverted-pressure").next_best_observation.observation_code, "repeat_blood_pressure")
        self.assertEqual(self.result("impossible-heart-rate").next_best_observation.observation_code, "repeat_heart_rate")


if __name__ == "__main__":
    unittest.main()
