"""Twenty-eight named edge cases for rules, product demos and regression tests."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .schemas import (
    ActorRole,
    ClinicianState,
    HistoryStatus,
    MedicalHistory,
    MentalStatus,
    Observation,
    ObservationQuality,
    ObservationSource,
    PatientState,
    Provenance,
    ProvenanceSource,
    QualityFlag,
    SexAtBirth,
    VitalValues,
)


BASE_TIME = datetime(2026, 1, 1, 8, tzinfo=timezone.utc)


SCENARIOS = [
    ("silent-hypoxia", 48, "shortness of breath", {"spo2_percent": 88}, ["ambiguous", "hard_red_flag"]),
    ("subtle-chest-pain", 54, "mild chest discomfort", {}, ["ambiguous"]),
    ("pediatric-fever-tachycardia", 5, "fever", {"heart_rate_bpm": 166, "temperature_c": 39.5}, ["pediatric", "hard_red_flag"]),
    ("infant-dehydration", 0.7, "vomiting and poor intake", {"systolic_bp_mmhg": 65}, ["pediatric", "hard_red_flag"]),
    ("geriatric-confusion", 81, "weakness", {"mental_status": "confused", "gcs": 14}, ["geriatric", "under_reported"]),
    ("frail-fall", 88, "minor fall", {}, ["geriatric", "frailty"]),
    ("no-record-chest-pain", 45, "chest pain", {}, ["zero_history", "ambiguous"]),
    ("underreported-stroke", 63, "feels odd", {}, ["under_reported", "hard_red_flag"]),
    ("worsening-respiration", 39, "cough", {"respiratory_rate_per_min": 30, "spo2_percent": 93}, ["worsening_waiting"]),
    ("falling-pressure", 67, "weakness", {"systolic_bp_mmhg": 94}, ["geriatric", "worsening_waiting"]),
    ("declining-consciousness", 32, "headache", {"gcs": 12}, ["worsening_waiting"]),
    ("wait-threshold-breach", 26, "abdominal pain", {}, ["wait_threshold"]),
    ("missing-spo2", 72, "shortness of breath", {"spo2_percent": None}, ["missing", "geriatric"]),
    ("missing-pressure", 17, "dizziness", {"systolic_bp_mmhg": None}, ["missing"]),
    ("inverted-pressure", 56, "weakness", {"systolic_bp_mmhg": 80, "diastolic_bp_mmhg": 95}, ["implausible"]),
    ("impossible-heart-rate", 41, "palpitations", {"heart_rate_bpm": 420}, ["implausible"]),
    ("stale-observation", 69, "fever", {}, ["stale", "geriatric"]),
    ("device-warning", 50, "shortness of breath", {}, ["device_warning"]),
    ("pregnancy-abdominal-pain", 30, "abdominal pain in pregnancy", {}, ["pregnancy", "ambiguous"]),
    ("severe-pain", 36, "severe abdominal pain", {"pain_score_0_10": 9}, ["urgent"]),
    ("stable-low-acuity", 22, "minor ankle pain", {"pain_score_0_10": 2}, ["stable"]),
    ("improving-after-rest", 60, "dizziness improving", {}, ["improving", "clinician_override_candidate"]),
    ("noisy-transient-reading", 47, "brief dizziness", {}, ["noisy", "clinician_override_candidate"]),
    ("unresponsive-adult", 44, "collapse", {"mental_status": "unresponsive", "gcs": 6}, ["hard_red_flag"]),
    ("active-bleeding", 28, "laceration", {}, ["hard_red_flag"]),
    ("possible-sepsis", 74, "fever and confusion", {"temperature_c": 40.1, "mental_status": "confused", "gcs": 14}, ["geriatric", "urgent"]),
    ("pediatric-stridor", 3, "noisy breathing", {}, ["pediatric", "hard_red_flag"]),
    ("adult-bradypnea", 59, "drowsiness", {"respiratory_rate_per_min": 6}, ["hard_red_flag"]),
]


def build_curated_cases() -> list[dict[str, object]]:
    cases = []
    for index, (scenario_id, age, complaint, updates, tags) in enumerate(SCENARIOS, start=1):
        arrival = BASE_TIME + timedelta(hours=index)
        baseline = VitalValues(
            heart_rate_bpm=88,
            respiratory_rate_per_min=18,
            spo2_percent=98,
            systolic_bp_mmhg=122,
            diastolic_bp_mmhg=78,
            temperature_c=37,
            gcs=15,
            pain_score_0_10=4,
            mental_status=MentalStatus.ALERT,
        )
        normalized_updates = dict(updates)
        if "mental_status" in normalized_updates:
            normalized_updates["mental_status"] = MentalStatus(normalized_updates["mental_status"])
        latest = baseline.model_copy(update=normalized_updates)
        flags = []
        if "missing" in tags:
            flags.append(QualityFlag.MISSING)
        if "implausible" in tags:
            flags.append(QualityFlag.IMPLAUSIBLE)
        if "device_warning" in tags:
            flags.append(QualityFlag.DEVICE_WARNING)
        observations = [
            Observation(
                observation_id=f"CUR-{index:02d}-1",
                recorded_at=arrival,
                source=ObservationSource.TRIAGE,
                values=baseline,
            )
        ]
        if "worsening_waiting" in tags or "improving" in tags or "noisy" in tags:
            observations.append(
                Observation(
                    observation_id=f"CUR-{index:02d}-2",
                    recorded_at=arrival + timedelta(minutes=25),
                    source=ObservationSource.REASSESSMENT,
                    values=latest,
                    quality=ObservationQuality(reliability=0.75 if "noisy" in tags else 0.95, flags=flags),
                )
            )
        else:
            observations[0] = observations[0].model_copy(
                update={"recorded_at": arrival - timedelta(minutes=40) if "stale" in tags else arrival, "values": latest, "quality": ObservationQuality(reliability=0.7 if flags else 0.95, flags=flags)}
            )
            if "stale" in tags:
                arrival = observations[0].recorded_at

        history_status = HistoryStatus.NONE if "zero_history" in tags else HistoryStatus.AVAILABLE
        history = MedicalHistory() if history_status == HistoryStatus.NONE else MedicalHistory(
            conditions=["hypertension"] if age >= 65 else [],
            frailty_score=8 if "frailty" in tags else None,
        )
        cues = []
        if scenario_id == "underreported-stroke":
            cues = ["stroke signs observed by nurse"]
        elif scenario_id == "active-bleeding":
            cues = ["uncontrolled bleeding"]
        elif scenario_id == "pediatric-stridor":
            cues = ["stridor"]
        assigned_level = 4 if "wait_threshold" in tags else 5 if scenario_id == "stable-low-acuity" else 3
        patient = PatientState(
            patient_id=f"P-{index:04d}",
            arrival_time=arrival,
            age_years=age,
            sex_at_birth=SexAtBirth.FEMALE if scenario_id == "pregnancy-abdominal-pain" else SexAtBirth.MALE,
            pregnancy_status="pregnant" if scenario_id == "pregnancy-abdominal-pain" else None,
            chief_complaint=complaint,
            reported_symptoms=[] if "under_reported" in tags else [complaint],
            observed_cues=cues,
            history_status=history_status,
            history=history,
            observations=observations,
            clinician_state=ClinicianState(assigned_level=assigned_level, assigned_by_role=ActorRole.SYSTEM_FIXTURE),
            provenance=Provenance(source=ProvenanceSource.SCRIPTED_FIXTURE, scenario_id=scenario_id),
        )
        evaluated_at = arrival + timedelta(minutes=65 if "wait_threshold" in tags else 40 if "stale" in tags else 25 if len(observations) > 1 else 0)
        cases.append({"scenario_id": scenario_id, "title": scenario_id.replace("-", " ").title(), "tags": tags, "evaluated_at": evaluated_at.isoformat(), "patient": patient.model_dump(mode="json")})
    return cases


def write_curated_cases(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_curated_cases(), indent=2) + "\n", encoding="utf-8")
