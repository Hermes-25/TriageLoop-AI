from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sqlite3
import unittest

from triageloop.product_store import ProductStore
from triageloop.schemas import PatientState, ProvenanceSource


class ProductStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.store = ProductStore(Path(self.temp.name) / "test.sqlite3")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_board_exposes_required_product_states(self) -> None:
        state = self.store.state()
        self.assertEqual(len(state["patients"]), 20)
        self.assertIn("capacity_conflicts", state["summary"])
        self.assertTrue(any(item["recommendation"]["uncertainty"] for item in state["patients"]))
        self.assertTrue(all("action_window" in item["recommendation"] for item in state["patients"]))

    def test_surge_recalculates_slack_and_keeps_capacity_truth_visible(self) -> None:
        baseline = self.store.state()["summary"]["capacity_conflicts"]
        surge = self.store.set_scenario("surge_3x")
        self.assertGreaterEqual(surge["summary"]["capacity_conflicts"], baseline)
        self.assertEqual(surge["capacity"]["state"], "constrained")

    def test_deterioration_moves_patient_and_creates_negative_slack(self) -> None:
        result = self.store.deteriorate("P-0009")
        self.assertEqual(result["queue_position"], 2)
        self.assertTrue(result["recommendation"]["capacity_conflict"])
        self.assertLess(result["recommendation"]["clinical_slack_minutes"], 0)
        self.assertGreaterEqual(len(result["recommendation"]["explanation"]["what_changed"]), 2)
        positions = [item["queue_position"] for item in self.store.state()["patients"]]
        self.assertEqual(positions, list(range(1, len(positions) + 1)))

    def test_explanation_uses_only_observed_positive_urgency_drivers(self) -> None:
        result = self.store.deteriorate("P-0009")
        factors = result["recommendation"]["explanation"]["top_factors"]
        self.assertTrue(any("oxygen saturation" in factor for factor in factors))
        self.assertFalse(any("confus" in factor.lower() for factor in factors))
        self.assertFalse(any("reduced estimated urgency" in factor for factor in factors))

    def test_override_requires_reason_and_is_hash_audited(self) -> None:
        with self.assertRaises(ValueError):
            self.store.record_decision("P-0009", "override", None, "continue monitored wait")
        result = self.store.record_decision("P-0009", "override", "Patient reviewed at bedside", "continue monitored wait")
        event = result["audit_event"]
        self.assertEqual(len(event["event_hash"]), 64)
        self.assertFalse(event["payload"]["autonomous_downgrade"])

    def test_compound_trigger_resolves_to_one_conservative_action(self) -> None:
        patient = self.store.patient("P-0008")
        recommendation = patient["recommendation"]
        self.assertTrue(recommendation["safety"]["safe_mode"])
        self.assertGreaterEqual(len(recommendation["safety"]["rule_hits"]), 1)
        self.assertEqual(recommendation["recommended_action"], "immediate_review")
        self.assertFalse(recommendation["safety"]["autonomous_downgrade_permitted"])

    def test_manual_json_intake_is_scored_queued_and_audited(self) -> None:
        fixtures = json.loads((self.store.root / "data" / "fixtures" / "curated-cases.json").read_text(encoding="utf-8"))
        source = next(case["patient"] for case in fixtures if case["patient"]["patient_id"] == "P-0009")
        source["patient_id"] = "P-99001"
        source["provenance"]["source"] = ProvenanceSource.MANUAL.value
        created = self.store.add_manual_patient(PatientState.model_validate(source))
        self.assertEqual(created["patient_id"], "P-99001")
        self.assertEqual(created["queue_position"], 21)
        self.assertTrue(created["recommendation"]["recommendation_id"])
        self.assertEqual(self.store.audit(patient_id="P-99001")[0]["event_type"], "manual_intake_created")

    def test_audit_chain_is_recomputed_and_tampering_is_detected(self) -> None:
        self.store.record_decision("P-0009", "override", "Bedside review", "continue monitored wait")
        self.assertTrue(self.store.verify_audit_chain()["intact"])
        connection = sqlite3.connect(self.store.database_path)
        try:
            connection.execute("UPDATE audit_events SET payload_json=? WHERE sequence=(SELECT MAX(sequence) FROM audit_events)", ('{"tampered":true}',))
            connection.commit()
        finally:
            connection.close()
        integrity = self.store.verify_audit_chain()
        self.assertFalse(integrity["intact"])
        self.assertIsNotNone(integrity["first_broken_sequence"])

    def test_evaluation_exposes_tl05_positive_and_negative_evidence(self) -> None:
        evidence = self.store.evaluation()
        self.assertIn("periodic_retriage", evidence)
        self.assertIn("nbo_verification", evidence)
        self.assertIn("external_plausibility", evidence)
        self.assertFalse(evidence["nbo_verification"]["gates"]["no_material_operational_recall_loss"])


if __name__ == "__main__":
    unittest.main()
