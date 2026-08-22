from datetime import datetime
import unittest

from triageloop.curated import build_curated_cases
from triageloop.safety import age_band, evaluate_safety
from triageloop.schemas import AgeBand, PatientState


def cases_by_id() -> dict[str, dict]:
    return {case["scenario_id"]: case for case in build_curated_cases()}


class SafetyGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = cases_by_id()

    def assess(self, scenario_id: str):
        case = self.cases[scenario_id]
        return evaluate_safety(PatientState.model_validate(case["patient"]), evaluated_at=datetime.fromisoformat(case["evaluated_at"]))

    def test_age_bands(self) -> None:
        self.assertEqual(age_band(11.99), AgeBand.PEDIATRIC)
        self.assertEqual(age_band(12), AgeBand.ADULT)
        self.assertEqual(age_band(65), AgeBand.GERIATRIC)

    def test_hard_red_flags_escalate_to_level_one(self) -> None:
        for scenario in ("silent-hypoxia", "pediatric-fever-tachycardia", "infant-dehydration", "unresponsive-adult", "pediatric-stridor", "adult-bradypnea"):
            with self.subTest(scenario=scenario):
                self.assertEqual(self.assess(scenario).recommended_level, 1)

    def test_worsening_waiting_patient_is_recalled(self) -> None:
        assessment = self.assess("worsening-respiration")
        self.assertTrue(assessment.reassessment_due)
        self.assertIn("WORSENING_TRAJECTORY", {hit.code for hit in assessment.rule_hits})

    def test_wait_threshold_triggers_reassessment(self) -> None:
        assessment = self.assess("wait-threshold-breach")
        self.assertIn("WAIT_THRESHOLD", {hit.code for hit in assessment.rule_hits})

    def test_bad_or_stale_data_activates_safe_mode(self) -> None:
        for scenario in ("missing-spo2", "missing-pressure", "inverted-pressure", "impossible-heart-rate", "stale-observation"):
            with self.subTest(scenario=scenario):
                self.assertTrue(self.assess(scenario).safe_mode)

    def test_no_autonomous_downgrade(self) -> None:
        for case in self.cases.values():
            patient = PatientState.model_validate(case["patient"])
            assessment = evaluate_safety(patient, evaluated_at=datetime.fromisoformat(case["evaluated_at"]))
            self.assertLessEqual(assessment.recommended_level, patient.clinician_state.assigned_level)
            self.assertFalse(assessment.autonomous_downgrade)


if __name__ == "__main__":
    unittest.main()
