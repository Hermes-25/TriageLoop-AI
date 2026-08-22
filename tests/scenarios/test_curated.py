import unittest

from triageloop.curated import build_curated_cases
from triageloop.schemas import PatientState


class CuratedScenarioTests(unittest.TestCase):
    def test_exactly_twenty_eight_unique_cases(self) -> None:
        cases = build_curated_cases()
        self.assertEqual(len(cases), 28)
        self.assertEqual(len({case["scenario_id"] for case in cases}), 28)

    def test_required_edge_case_coverage(self) -> None:
        tags = {tag for case in build_curated_cases() for tag in case["tags"]}
        required = {
            "ambiguous",
            "pediatric",
            "geriatric",
            "zero_history",
            "under_reported",
            "worsening_waiting",
            "missing",
            "implausible",
            "clinician_override_candidate",
        }
        self.assertTrue(required.issubset(tags), required - tags)

    def test_every_case_conforms_to_patient_contract(self) -> None:
        for case in build_curated_cases():
            with self.subTest(scenario=case["scenario_id"]):
                PatientState.model_validate(case["patient"])


if __name__ == "__main__":
    unittest.main()
