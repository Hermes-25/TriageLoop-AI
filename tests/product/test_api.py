from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fastapi.testclient import TestClient

from triageloop.api import create_app


ROOT = Path(__file__).resolve().parents[2]


class ProductApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.client = TestClient(create_app(Path(self.temp.name) / "api.sqlite3"))

    def tearDown(self) -> None:
        self.client.close()
        self.temp.cleanup()

    def test_manual_synthetic_intake_endpoint(self) -> None:
        fixtures = json.loads((ROOT / "data" / "fixtures" / "curated-cases.json").read_text(encoding="utf-8"))
        payload = next(case["patient"] for case in fixtures if case["patient"]["patient_id"] == "P-0009")
        payload["patient_id"] = "P-99002"
        payload["provenance"]["source"] = "manual"

        response = self.client.post("/v1/intake/manual", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["patient_id"], "P-99002")
        self.assertTrue(response.json()["recommendation"]["recommendation_id"])

    def test_manual_intake_rejects_non_manual_provenance(self) -> None:
        fixtures = json.loads((ROOT / "data" / "fixtures" / "curated-cases.json").read_text(encoding="utf-8"))
        payload = next(case["patient"] for case in fixtures if case["patient"]["patient_id"] == "P-0009")
        payload["patient_id"] = "P-99003"

        response = self.client.post("/v1/intake/manual", json=payload)

        self.assertEqual(response.status_code, 422)
        self.assertIn("provenance.source=manual", response.json()["detail"])

    def test_manual_intake_rejects_real_or_directly_identifying_payloads(self) -> None:
        fixtures = json.loads((ROOT / "data" / "fixtures" / "curated-cases.json").read_text(encoding="utf-8"))
        payload = next(case["patient"] for case in fixtures if case["patient"]["patient_id"] == "P-0009")
        payload["patient_id"] = "P-99004"
        payload["provenance"]["source"] = "manual"
        payload["provenance"]["synthetic"] = False
        payload["patient_name"] = "Direct Identifier"
        response = self.client.post("/v1/intake/manual", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_cors_is_allowlisted_and_unsupported_methods_fail_closed(self) -> None:
        allowed = self.client.get("/v1/health", headers={"Origin": "http://localhost:3000"})
        rejected = self.client.get("/v1/health", headers={"Origin": "https://malicious.example"})
        self.assertEqual(allowed.headers.get("access-control-allow-origin"), "http://localhost:3000")
        self.assertIsNone(rejected.headers.get("access-control-allow-origin"))
        self.assertEqual(self.client.delete("/v1/demo/reset").status_code, 405)

    def test_decision_reason_length_and_audit_integrity_endpoint(self) -> None:
        too_long = self.client.post(
            "/v1/patients/P-0009/decisions",
            json={"action": "override", "reason": "x" * 501, "modified_action": "wait"},
        )
        self.assertEqual(too_long.status_code, 422)
        integrity = self.client.get("/v1/audit/integrity")
        self.assertEqual(integrity.status_code, 200)
        self.assertTrue(integrity.json()["intact"])


if __name__ == "__main__":
    unittest.main()
