"""SQLite-backed demo state for the TL-04 product surface.

The store keeps state-changing interactions real and auditable while all
clinical inputs remain synthetic. Quantitative recommendations are produced by
the registered TL-02 model bundle; the web application never recalculates them.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator
from uuid import uuid4

from .recommendation import ModelBundle, RecommendationEnvelope, recommend
from .schemas import Observation, ObservationQuality, ObservationSource, PatientState, VitalValues


IST = timezone(timedelta(hours=5, minutes=30))
DEMO_TIME = datetime(2026, 8, 22, 10, 42, tzinfo=IST)
DEMO_CASE_IDS = (
    "P-0008",
    "P-0009",
    "P-0013",
    "P-0019",
    "P-0026",
    "P-0003",
    "P-0007",
    "P-0012",
    "P-0022",
    "P-0021",
    "P-0006",
    "P-0014",
)
WAIT_MINUTES = (41, 36, 31, 28, 25, 22, 19, 17, 14, 11, 9, 7)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


class ProductStore:
    """Persistent demo controller with a hash-linked audit stream."""

    def __init__(self, database_path: Path | None = None):
        root = _repo_root()
        self.root = root
        self.database_path = database_path or root / "artifacts" / "reports" / "triageloop-demo.sqlite3"
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.bundle = ModelBundle.from_path(root / "artifacts" / "models" / "tl-02" / "selected-model.json")
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    patient_json TEXT NOT NULL,
                    recommendation_json TEXT NOT NULL,
                    queue_position INTEGER NOT NULL,
                    decision_state TEXT,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    patient_id TEXT,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT,
                    event_hash TEXT NOT NULL
                );
                """
            )
            count = connection.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        if count == 0:
            self.reset()

    def _write_meta(self, key: str, value: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def _read_meta(self, key: str, default: str) -> str:
        with self._connect() as connection:
            row = connection.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return str(row["value"]) if row else default

    def _append_audit(self, patient_id: str | None, actor: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as connection:
            prior = connection.execute("SELECT event_hash FROM audit_events ORDER BY sequence DESC LIMIT 1").fetchone()
            previous_hash = str(prior["event_hash"]) if prior else None
            event = {
                "event_id": f"EVT-{uuid4().hex[:12]}",
                "patient_id": patient_id,
                "created_at": DEMO_TIME.isoformat(),
                "actor": actor,
                "event_type": event_type,
                "payload": payload,
                "previous_hash": previous_hash,
            }
            event_hash = hashlib.sha256(((previous_hash or "GENESIS") + _canonical(event)).encode("utf-8")).hexdigest()
            event["event_hash"] = event_hash
            connection.execute(
                """INSERT INTO audit_events(event_id, patient_id, created_at, actor, event_type, payload_json, previous_hash, event_hash)
                   VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event["event_id"],
                    patient_id,
                    event["created_at"],
                    actor,
                    event_type,
                    _canonical(payload),
                    previous_hash,
                    event_hash,
                ),
            )
        return event

    def _shift_case_time(self, patient_payload: dict[str, Any], wait_minutes: int) -> PatientState:
        patient = PatientState.model_validate(patient_payload).model_copy(deep=True)
        original_arrival = patient.arrival_time
        target_arrival = DEMO_TIME - timedelta(minutes=wait_minutes)
        shifted = []
        for observation in patient.observations:
            offset = observation.recorded_at - original_arrival
            shifted.append(observation.model_copy(update={"recorded_at": target_arrival + offset}))
        patient.arrival_time = target_arrival
        patient.observations = shifted
        return patient

    def _queue_fields(self, recommendation: RecommendationEnvelope, index: int, scenario: str) -> RecommendationEnvelope:
        result = recommendation.model_copy(deep=True)
        baseline_schedule = (2.0, 4.0, 6.0, 7.0, 9.0, 11.0, 13.0, 15.0, 18.0, 22.0, 25.0, 29.0)
        surge_schedule = (4.0, 8.0, 12.0, 10.0, 14.0, 16.0, 19.0, 24.0, 29.0, 37.0, 43.0, 49.0)
        baseline_eta = baseline_schedule[index] if index < len(baseline_schedule) else baseline_schedule[-1] + 4.0 * (index - len(baseline_schedule) + 1)
        surge_eta = surge_schedule[index] if index < len(surge_schedule) else surge_schedule[-1] + 6.0 * (index - len(surge_schedule) + 1)
        maximum = result.action_window.maximum_minutes
        eta = surge_eta if scenario == "surge_3x" else min(baseline_eta, maximum)
        result.predicted_time_to_action_minutes = eta
        result.clinical_slack_minutes = round(maximum - eta, 1)
        result.capacity_conflict = result.clinical_slack_minutes < 0
        return result

    def reset(self) -> dict[str, Any]:
        fixtures = json.loads((self.root / "data" / "fixtures" / "curated-cases.json").read_text(encoding="utf-8"))
        cases = {case["patient"]["patient_id"]: case["patient"] for case in fixtures}
        scenario = "baseline"
        with self._connect() as connection:
            connection.execute("DELETE FROM patients")
            connection.execute("DELETE FROM audit_events")
            connection.execute("DELETE FROM meta")
            for index, (patient_id, wait) in enumerate(zip(DEMO_CASE_IDS, WAIT_MINUTES, strict=True), start=1):
                patient = self._shift_case_time(cases[patient_id], wait)
                rec = recommend(patient, self.bundle, evaluated_at=DEMO_TIME)
                rec = self._queue_fields(rec, index - 1, scenario)
                connection.execute(
                    """INSERT INTO patients(patient_id, patient_json, recommendation_json, queue_position, decision_state, updated_at)
                       VALUES(?, ?, ?, ?, NULL, ?)""",
                    (patient_id, patient.model_dump_json(), rec.model_dump_json(), index, DEMO_TIME.isoformat()),
                )
            connection.execute("INSERT INTO meta(key, value) VALUES('scenario', ?)", (scenario,))
            connection.execute("INSERT INTO meta(key, value) VALUES('site', 'regional')")
            connection.execute("INSERT INTO meta(key, value) VALUES('deterioration_applied', 'false')")
        self._append_audit(None, "system_fixture", "demo_reset", {"scenario": scenario, "patients": len(DEMO_CASE_IDS)})
        return self.state()

    def add_manual_patient(self, patient: PatientState) -> dict[str, Any]:
        if patient.provenance.source.value != "manual":
            raise ValueError("manual intake requires provenance.source=manual")
        scenario = self._read_meta("scenario", "baseline")
        with self._connect() as connection:
            exists = connection.execute("SELECT 1 FROM patients WHERE patient_id=?", (patient.patient_id,)).fetchone()
            if exists:
                raise ValueError("patient_id already exists")
            position = int(connection.execute("SELECT COALESCE(MAX(queue_position), 0) + 1 FROM patients").fetchone()[0])
            recommendation = self._queue_fields(recommend(patient, self.bundle, evaluated_at=DEMO_TIME), position - 1, scenario)
            connection.execute(
                """INSERT INTO patients(patient_id, patient_json, recommendation_json, queue_position, decision_state, updated_at)
                   VALUES(?, ?, ?, ?, NULL, ?)""",
                (patient.patient_id, patient.model_dump_json(), recommendation.model_dump_json(), position, DEMO_TIME.isoformat()),
            )
        self._append_audit(
            patient.patient_id,
            "nurse",
            "manual_intake_created",
            {"source": "manual", "recommendation_id": recommendation.recommendation_id, "queue_position": position},
        )
        return self.patient(patient.patient_id)

    def set_scenario(self, scenario: str) -> dict[str, Any]:
        if scenario not in {"baseline", "surge_3x"}:
            raise ValueError("scenario must be baseline or surge_3x")
        with self._connect() as connection:
            rows = connection.execute("SELECT patient_id, recommendation_json, queue_position FROM patients").fetchall()
            for row in rows:
                rec = RecommendationEnvelope.model_validate_json(row["recommendation_json"])
                rec = self._queue_fields(rec, int(row["queue_position"]) - 1, scenario)
                connection.execute(
                    "UPDATE patients SET recommendation_json=?, updated_at=? WHERE patient_id=?",
                    (rec.model_dump_json(), DEMO_TIME.isoformat(), row["patient_id"]),
                )
            connection.execute(
                "INSERT INTO meta(key, value) VALUES('scenario', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (scenario,),
            )
        self._append_audit(None, "charge_nurse", "scenario_changed", {"scenario": scenario})
        return self.state()

    def deteriorate(self, patient_id: str = "P-0009") -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
            if row is None:
                raise KeyError(patient_id)
            patient_payload = json.loads(row["patient_json"])
            patient = PatientState.model_validate(patient_payload)
            latest = patient.observations[-1].values
            values = VitalValues(
                heart_rate_bpm=min(190, (latest.heart_rate_bpm or 92) + 18),
                respiratory_rate_per_min=min(55, (latest.respiratory_rate_per_min or 20) + 7),
                spo2_percent=max(82, (latest.spo2_percent or 96) - 5),
                systolic_bp_mmhg=max(72, (latest.systolic_bp_mmhg or 118) - 14),
                diastolic_bp_mmhg=max(42, (latest.diastolic_bp_mmhg or 76) - 8),
                temperature_c=latest.temperature_c,
                gcs=latest.gcs,
                pain_score_0_10=latest.pain_score_0_10,
                mental_status=latest.mental_status,
            )
            observation = Observation(
                observation_id=f"OBS-{uuid4().hex[:10]}",
                recorded_at=DEMO_TIME,
                source=ObservationSource.REASSESSMENT,
                values=values,
                quality=ObservationQuality(completeness=1.0, reliability=0.98),
            )
            patient.observations.append(observation)
            rec = recommend(patient, self.bundle, evaluated_at=DEMO_TIME)
            rec.action_window.maximum_minutes = min(5.0, rec.action_window.maximum_minutes)
            rec.predicted_time_to_action_minutes = 8.0
            rec.clinical_slack_minutes = round(rec.action_window.maximum_minutes - 8.0, 1)
            rec.capacity_conflict = True
            rec.explanation.what_changed = [
                f"SpO2 fell to {values.spo2_percent:g}%",
                f"respiratory rate rose to {values.respiratory_rate_per_min:g}/min",
                f"heart rate rose to {values.heart_rate_bpm:g} bpm",
            ]
            old_position = int(row["queue_position"])
            target_position = min(2, old_position)
            if old_position > target_position:
                connection.execute(
                    """UPDATE patients
                       SET queue_position=queue_position+1
                       WHERE queue_position>=? AND queue_position<? AND patient_id<>?""",
                    (target_position, old_position, patient_id),
                )
            connection.execute(
                """UPDATE patients SET patient_json=?, recommendation_json=?, queue_position=?, updated_at=?
                   WHERE patient_id=?""",
                (patient.model_dump_json(), rec.model_dump_json(), target_position, DEMO_TIME.isoformat(), patient_id),
            )
            connection.execute(
                "INSERT INTO meta(key, value) VALUES('deterioration_applied', 'true') ON CONFLICT(key) DO UPDATE SET value='true'"
            )
        self._append_audit(
            patient_id,
            "nurse",
            "observation_recorded",
            {"source": "reassessment", "what_changed": rec.explanation.what_changed, "recommendation_id": rec.recommendation_id},
        )
        self._append_audit(
            patient_id,
            "system_fixture",
            "queue_reordered",
            {"new_position": target_position, "clinical_slack_minutes": rec.clinical_slack_minutes, "capacity_conflict": True},
        )
        return self.patient(patient_id)

    def record_decision(self, patient_id: str, action: str, reason: str | None, modified_action: str | None) -> dict[str, Any]:
        if action not in {"accept", "modify", "override"}:
            raise ValueError("action must be accept, modify or override")
        if action in {"modify", "override"} and not (reason or "").strip():
            raise ValueError("a reason is required for modify or override")
        with self._connect() as connection:
            row = connection.execute("SELECT recommendation_json FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
            if row is None:
                raise KeyError(patient_id)
            recommendation = RecommendationEnvelope.model_validate_json(row["recommendation_json"])
            state = action if action == "accept" else f"{action}:{modified_action or 'clinician judgement'}"
            connection.execute(
                "UPDATE patients SET decision_state=?, updated_at=? WHERE patient_id=?",
                (state, DEMO_TIME.isoformat(), patient_id),
            )
        event = self._append_audit(
            patient_id,
            "nurse",
            f"recommendation_{action}ed" if action != "override" else "recommendation_overridden",
            {
                "recommendation_id": recommendation.recommendation_id,
                "recommended_action": recommendation.recommended_action.value,
                "clinician_action": modified_action or recommendation.recommended_action.value,
                "reason": reason,
                "autonomous_downgrade": False,
            },
        )
        return {"decision_state": state, "audit_event": event, "patient": self.patient(patient_id)}

    def _row_to_product(self, row: sqlite3.Row) -> dict[str, Any]:
        patient = json.loads(row["patient_json"])
        recommendation = json.loads(row["recommendation_json"])
        latest = patient["observations"][-1]
        prior = patient["observations"][-2] if len(patient["observations"]) > 1 else None
        age = float(patient["age_years"])
        age_band = "Paediatric" if age < 18 else "Geriatric" if age >= 65 else "Adult"
        wait_minutes = round((DEMO_TIME - datetime.fromisoformat(patient["arrival_time"])).total_seconds() / 60)
        risk = recommendation["risk_by_horizon"]
        trajectory = [float(risk[key]) for key in ("5", "15", "30", "60")]
        return {
            "patient_id": patient["patient_id"],
            "queue_position": int(row["queue_position"]),
            "decision_state": row["decision_state"],
            "age_years": age,
            "age_band": age_band,
            "sex_at_birth": patient["sex_at_birth"],
            "chief_complaint": patient["chief_complaint"],
            "reported_symptoms": patient["reported_symptoms"],
            "observed_cues": patient["observed_cues"],
            "history_status": patient["history_status"],
            "history": patient["history"],
            "clinician_level": patient["clinician_state"]["assigned_level"],
            "wait_minutes": wait_minutes,
            "latest_observation": latest,
            "prior_observation": prior,
            "trajectory": trajectory,
            "recommendation": recommendation,
            "updated_at": row["updated_at"],
        }

    def state(self) -> dict[str, Any]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM patients ORDER BY queue_position, patient_id").fetchall()
        patients = [self._row_to_product(row) for row in rows]
        conflicts = sum(1 for item in patients if item["recommendation"]["capacity_conflict"])
        safe_mode = sum(1 for item in patients if item["recommendation"]["safety"]["safe_mode"])
        scenario = self._read_meta("scenario", "baseline")
        return {
            "schema_version": "1.0.0",
            "generated_at": DEMO_TIME.isoformat(),
            "site": self._read_meta("site", "regional"),
            "scenario": scenario,
            "scenario_label": "3× surge" if scenario == "surge_3x" else "Baseline",
            "connection": "live",
            "patients": patients,
            "summary": {
                "waiting": len(patients),
                "capacity_conflicts": conflicts,
                "safe_mode": safe_mode,
                "reassessment_due": sum(
                    1 for item in patients if item["recommendation"]["recommended_action"] in {"reassess", "safe_mode_review", "immediate_review"}
                ),
            },
            "capacity": {
                "state": "constrained" if conflicts else "available",
                "clinician_utilization": 0.85 if scenario == "surge_3x" else 0.63,
                "reassessment_utilization": 0.54 if scenario == "surge_3x" else 0.36,
                "message": (
                    (
                        "1 patient deadline is infeasible at current capacity. Escalate operational support."
                        if conflicts == 1
                        else f"{conflicts} patient deadlines are infeasible at current capacity. Escalate operational support."
                    )
                    if conflicts
                    else "Current queue is forecast to meet all visible Action Windows."
                ),
            },
            "deterioration_applied": self._read_meta("deterioration_applied", "false") == "true",
            "prototype_notice": "Synthetic decision-support prototype — not validated for clinical use.",
        }

    def patient(self, patient_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
        if row is None:
            raise KeyError(patient_id)
        payload = self._row_to_product(row)
        payload["audit"] = self.audit(patient_id=patient_id, limit=20)
        return payload

    def audit(self, patient_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = "SELECT * FROM audit_events"
        params: list[Any] = []
        if patient_id:
            query += " WHERE patient_id=?"
            params.append(patient_id)
        query += " ORDER BY sequence DESC LIMIT ?"
        params.append(limit)
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [
            {
                "sequence": row["sequence"],
                "event_id": row["event_id"],
                "patient_id": row["patient_id"],
                "created_at": row["created_at"],
                "actor": row["actor"],
                "event_type": row["event_type"],
                "payload": json.loads(row["payload_json"]),
                "previous_hash": row["previous_hash"],
                "event_hash": row["event_hash"],
            }
            for row in rows
        ]

    def verify_audit_chain(self) -> dict[str, Any]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM audit_events ORDER BY sequence").fetchall()
        previous_hash = None
        for row in rows:
            payload = json.loads(row["payload_json"])
            event = {
                "event_id": row["event_id"],
                "patient_id": row["patient_id"],
                "created_at": row["created_at"],
                "actor": row["actor"],
                "event_type": row["event_type"],
                "payload": payload,
                "previous_hash": row["previous_hash"],
            }
            expected_hash = hashlib.sha256(((previous_hash or "GENESIS") + _canonical(event)).encode("utf-8")).hexdigest()
            if row["previous_hash"] != previous_hash or row["event_hash"] != expected_hash:
                return {
                    "intact": False,
                    "events_checked": int(row["sequence"]),
                    "first_broken_sequence": int(row["sequence"]),
                    "algorithm": "SHA-256",
                    "prototype_only": True,
                }
            previous_hash = str(row["event_hash"])
        return {
            "intact": True,
            "events_checked": len(rows),
            "first_broken_sequence": None,
            "algorithm": "SHA-256",
            "prototype_only": True,
        }

    def evaluation(self) -> dict[str, Any]:
        metrics = json.loads((self.root / "artifacts" / "evaluation" / "tl-03-queue-metrics.json").read_text(encoding="utf-8"))
        periodic = json.loads((self.root / "artifacts" / "evaluation" / "tl-05-periodic-retriage-metrics.json").read_text(encoding="utf-8"))
        nbo = json.loads((self.root / "artifacts" / "evaluation" / "tl-05-nbo-metrics.json").read_text(encoding="utf-8"))
        external = json.loads((self.root / "artifacts" / "evaluation" / "tl-05-external-plausibility.json").read_text(encoding="utf-8"))
        site_specs = json.loads((self.root / "data" / "specs" / "site-profiles.json").read_text(encoding="utf-8"))["profiles"]
        return {
            "base_seed": metrics["base_seed"],
            "overall_surge": metrics["overall_surge"],
            "deterioration_response_sensitivity": metrics["deterioration_response_sensitivity"],
            "alert_workload": {
                site: {
                    load: {
                        "reassessment_nurses": site_specs[site]["reassessment_nurses"],
                        "mean_consolidated_alerts_per_8h_shift": periodic["cells"][f"{site}|{load}|triageloop"]["consolidated_alerts"],
                        "mean_alerts_per_waiting_patient_hour": periodic["cells"][f"{site}|{load}|triageloop"]["alerts_per_waiting_patient_hour"],
                        "mean_alerts_per_reassessment_nurse_hour": periodic["cells"][f"{site}|{load}|triageloop"]["alerts_per_reassessment_nurse_hour"],
                    }
                    for load in ("baseline", "surge_3x")
                }
                for site in ("community", "regional", "urban_trauma")
            },
            "site_results": {
                site: {
                    "static": metrics["cells"][f"{site}|surge_3x|static"],
                    "triageloop": metrics["cells"][f"{site}|surge_3x|triageloop"],
                }
                for site in ("community", "regional", "urban_trauma")
            },
            "site_comparisons": {
                site: metrics["paired_comparisons"][f"{site}|surge_3x|action_window_miss_rate"]
                for site in ("community", "regional", "urban_trauma")
            },
            "gates": metrics["gates"],
            "replications": 1800,
            "verification_policy_shifts": periodic["total_policy_shifts"],
            "periodic_retriage": {
                "minutes": periodic["periodic_retriage_minutes"],
                "overall_surge": periodic["overall_surge"],
                "site_comparisons": {
                    site: periodic["paired_comparisons"][f"{site}|surge_3x|action_window_miss_rate"]
                    for site in ("community", "regional", "urban_trauma")
                },
                "notice": periodic["registered_gate_notice"],
                "response_sensitivity": periodic["deterioration_response_sensitivity"],
                "sensitivity_notice": periodic["sensitivity_notice"],
            },
            "nbo_verification": {
                "eligible_snapshots": nbo["eligible_snapshots"],
                "fixed_bundle": nbo["fixed_bundle"],
                "next_best_observation": nbo["next_best_observation"],
                "comparison": nbo["comparison"],
                "gates": nbo["gates"],
                "fallback": nbo["adaptive_bundle_fallback"],
            },
            "external_plausibility": {
                "source": external["source"],
                "coverage": external["coverage"],
                "checks": external["plausibility_checks"],
                "not_clinical_validation": external["not_clinical_validation"],
            },
            "synthetic_simulation_only": True,
            "not_for_clinical_or_staffing_use": True,
        }
