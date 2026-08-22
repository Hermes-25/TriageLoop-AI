from datetime import datetime, timedelta, timezone
import unittest

from pydantic import ValidationError

from triageloop.schemas import (
    ClinicianState,
    HistoryStatus,
    Observation,
    ObservationSource,
    PatientState,
    Provenance,
    ProvenanceSource,
    SexAtBirth,
    VitalValues,
)


def valid_patient() -> PatientState:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return PatientState(
        patient_id="P-001",
        arrival_time=now,
        age_years=35,
        sex_at_birth=SexAtBirth.FEMALE,
        chief_complaint="dizziness",
        history_status=HistoryStatus.NONE,
        observations=[Observation(observation_id="O-1", recorded_at=now, source=ObservationSource.TRIAGE, values=VitalValues())],
        clinician_state=ClinicianState(assigned_level=3),
        provenance=Provenance(source=ProvenanceSource.SCRIPTED_FIXTURE),
    )


class PatientContractTests(unittest.TestCase):
    def test_valid_contract_round_trip(self) -> None:
        patient = valid_patient()
        reparsed = PatientState.model_validate_json(patient.model_dump_json())
        self.assertEqual(reparsed.schema_version, "1.0.0")

    def test_rejects_unknown_fields(self) -> None:
        payload = valid_patient().model_dump(mode="json")
        payload["future_field"] = "unsafe"
        with self.assertRaises(ValidationError):
            PatientState.model_validate(payload)

    def test_rejects_observation_before_arrival(self) -> None:
        patient = valid_patient()
        payload = patient.model_dump(mode="python")
        payload["observations"][0]["recorded_at"] = patient.arrival_time - timedelta(minutes=1)
        with self.assertRaises(ValidationError):
            PatientState.model_validate(payload)

    def test_zero_history_cannot_leak_prior_records(self) -> None:
        payload = valid_patient().model_dump(mode="python")
        payload["history"]["conditions"] = ["asthma"]
        with self.assertRaises(ValidationError):
            PatientState.model_validate(payload)


if __name__ == "__main__":
    unittest.main()
