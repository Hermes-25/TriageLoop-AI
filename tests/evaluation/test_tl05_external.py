import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class TL05ExternalPlausibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "artifacts" / "evaluation" / "tl-05-external-plausibility.json"
        if not path.exists():
            raise unittest.SkipTest("run TL-05 external plausibility check first")
        cls.results = json.loads(path.read_text(encoding="utf-8"))

    def test_external_source_and_nonvalidation_boundary_are_explicit(self) -> None:
        self.assertEqual(self.results["source"]["version"], "2.2")
        self.assertTrue(self.results["externally_sourced_deidentified_data"])
        self.assertTrue(self.results["not_clinical_validation"])
        self.assertIn("not an emergency-department cohort", self.results["source"]["population"])

    def test_all_core_vital_fields_are_present(self) -> None:
        self.assertTrue(self.results["plausibility_checks"]["all_five_core_vital_fields_present"])
        self.assertGreater(self.results["coverage"]["external_measurements"], 0)


if __name__ == "__main__":
    unittest.main()
