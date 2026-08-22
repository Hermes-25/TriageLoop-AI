"""Reproducible longitudinal synthetic data for prototype development only."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
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
    SyntheticEncounter,
    SyntheticTruth,
    VitalValues,
)


GENERATOR_VERSION = "1.0.0"
DEFAULT_SEED = 20260821


@dataclass(frozen=True)
class GeneratorConfig:
    seed: int = DEFAULT_SEED
    total_encounters: int = 10_000
    stress_encounters: int = 500
    max_observations: int = 4


COMPLAINTS = (
    "shortness of breath",
    "chest discomfort",
    "abdominal pain",
    "fever and weakness",
    "dizziness",
    "fall with pain",
    "vomiting and poor intake",
    "headache",
    "cough",
    "generalised weakness",
)


def _clip(value: float, lower: float, upper: float) -> float:
    return round(min(upper, max(lower, value)), 1)


def _baseline(age: float) -> tuple[float, float, float, float, float, float]:
    if age < 1:
        return 130, 32, 98, 85, 55, 37.0
    if age < 12:
        return 96, 22, 98, 102, 66, 37.0
    if age < 65:
        return 79, 16, 98, 122, 78, 36.9
    return 75, 17, 97, 132, 74, 36.8


def _draw_age(rng: random.Random) -> float:
    group = rng.choices(("pediatric", "adult", "geriatric"), weights=(15, 60, 25), k=1)[0]
    if group == "pediatric":
        return round(rng.uniform(0.08, 11.99), 2)
    if group == "adult":
        return round(rng.uniform(12, 64.99), 1)
    return round(rng.uniform(65, 95), 1)


def _history(rng: random.Random, age: float) -> tuple[HistoryStatus, MedicalHistory]:
    status = rng.choices(
        (HistoryStatus.NONE, HistoryStatus.PARTIAL, HistoryStatus.AVAILABLE),
        weights=(50, 20, 30),
        k=1,
    )[0]
    if status == HistoryStatus.NONE:
        return status, MedicalHistory()
    conditions = rng.sample(
        ["hypertension", "diabetes", "asthma", "chronic kidney disease", "heart failure"],
        k=rng.randint(0, 2),
    )
    return status, MedicalHistory(
        conditions=conditions,
        medications=["regular medication"] if status == HistoryStatus.AVAILABLE and conditions else [],
        allergies=["unknown"] if status == HistoryStatus.PARTIAL and rng.random() < 0.3 else [],
        frailty_score=rng.randint(3, 8) if age >= 65 and status == HistoryStatus.AVAILABLE else None,
    )


def _trajectory(rng: random.Random, *, stress: bool) -> tuple[str, int | None]:
    if stress:
        kind = rng.choices(("rapid_deterioration", "slow_deterioration", "noisy"), weights=(45, 35, 20), k=1)[0]
    else:
        kind = rng.choices(
            ("stable", "recovery", "noisy", "slow_deterioration", "rapid_deterioration"),
            weights=(58, 12, 10, 14, 6),
            k=1,
        )[0]
    if kind == "rapid_deterioration":
        return kind, rng.choices((5, 15, 30), weights=(25, 50, 25), k=1)[0]
    if kind == "slow_deterioration":
        return kind, rng.choices((30, 60, None), weights=(30, 50, 20), k=1)[0]
    return kind, None


def _split(index: int, base_count: int, stress: bool) -> str:
    if stress:
        return "stress"
    marker = index / base_count
    if marker < 0.6:
        return "train"
    if marker < 0.8:
        return "validation"
    return "test"


def generate_encounter(index: int, rng: random.Random, *, base_count: int, stress: bool = False) -> SyntheticEncounter:
    age = _draw_age(rng)
    history_status, history = _history(rng, age)
    trajectory, event_minute = _trajectory(rng, stress=stress)
    arrival = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index * 3)
    hr, rr, spo2, sbp, dbp, temp = _baseline(age)
    observations = []
    count = rng.randint(2, 4)
    interval_minutes = rng.choice((10, 15, 20))
    missing_probability = 0.18 if stress else 0.05
    for step in range(count):
        minute = step * interval_minutes
        direction = 0
        if trajectory == "rapid_deterioration":
            direction = step * 1.7
        elif trajectory == "slow_deterioration":
            direction = step * 0.8
        elif trajectory == "recovery":
            direction = -step * 0.5
        elif trajectory == "noisy":
            direction = rng.uniform(-1.2, 1.2)

        values = VitalValues(
            heart_rate_bpm=_clip(hr + rng.gauss(0, 7) + 8 * direction, 25, 260),
            respiratory_rate_per_min=_clip(rr + rng.gauss(0, 2) + 3 * direction, 4, 80),
            spo2_percent=_clip(spo2 + rng.gauss(0, 1) - 2.5 * max(0, direction), 55, 100),
            systolic_bp_mmhg=_clip(sbp + rng.gauss(0, 8) - 8 * max(0, direction), 40, 260),
            diastolic_bp_mmhg=_clip(dbp + rng.gauss(0, 5) - 4 * max(0, direction), 25, 180),
            temperature_c=_clip(temp + rng.gauss(0, 0.5) + 0.3 * max(0, direction), 32, 43),
            gcs=_clip(15 - round(max(0, direction) / 1.7), 3, 15),
            pain_score_0_10=_clip(rng.uniform(0, 8) + max(0, direction), 0, 10),
            mental_status=MentalStatus.ALERT if direction < 1.5 else MentalStatus.CONFUSED,
        )
        flags: list[QualityFlag] = []
        if rng.random() < missing_probability:
            missing_field = rng.choice(("spo2_percent", "systolic_bp_mmhg", "temperature_c"))
            values = values.model_copy(update={missing_field: None})
            flags.append(QualityFlag.MISSING)
        if stress and rng.random() < 0.08:
            values = values.model_copy(update={"heart_rate_bpm": 420.0})
            flags.append(QualityFlag.IMPLAUSIBLE)
        vital_fields = type(values).model_fields
        completeness = sum(getattr(values, field) is not None for field in vital_fields) / len(vital_fields)
        observations.append(
            Observation(
                observation_id=f"OBS-{index:06d}-{step + 1}",
                recorded_at=arrival + timedelta(minutes=minute),
                source=ObservationSource.TRIAGE if step == 0 else ObservationSource.SYNTHETIC_EVENT,
                values=values,
                quality=ObservationQuality(completeness=completeness, reliability=0.7 if flags else 0.95, flags=flags),
            )
        )

    assigned_level = rng.choices((2, 3, 4, 5), weights=(10, 45, 35, 10), k=1)[0]
    if event_minute is not None and event_minute <= 15 and rng.random() < 0.7:
        assigned_level = min(assigned_level, 2)
    patient = PatientState(
        patient_id=f"P-{index + 1:06d}",
        arrival_time=arrival,
        age_years=age,
        sex_at_birth=rng.choice(list(SexAtBirth)[:2]),
        chief_complaint=rng.choice(COMPLAINTS),
        reported_symptoms=[] if rng.random() < 0.12 else ["patient-reported symptom"],
        observed_cues=["appears unwell"] if stress and rng.random() < 0.25 else [],
        history_status=history_status,
        history=history,
        observations=observations,
        clinician_state=ClinicianState(assigned_level=assigned_level, assigned_by_role=ActorRole.SYSTEM_FIXTURE),
        provenance=Provenance(source=ProvenanceSource.SYNTHETIC_GENERATOR, generator_version=GENERATOR_VERSION),
    )
    event = event_minute if event_minute is not None else 10_000
    minimum_level = 1 if event <= 15 else 2 if event <= 60 else min(assigned_level, 4)
    return SyntheticEncounter(
        encounter_id=f"E-{index + 1:08d}",
        patient=patient,
        truth=SyntheticTruth(
            trajectory_type=trajectory,
            critical_within_5m=event <= 5,
            critical_within_15m=event <= 15,
            critical_within_30m=event <= 30,
            critical_within_60m=event <= 60,
            minimum_level=minimum_level,
            split=_split(index, base_count, stress),
        ),
        tags=[trajectory] + (["stress"] if stress else []) + (["zero_history"] if history_status == HistoryStatus.NONE else []),
    )


def generate_dataset(config: GeneratorConfig = GeneratorConfig()) -> list[SyntheticEncounter]:
    if config.stress_encounters >= config.total_encounters:
        raise ValueError("stress_encounters must be smaller than total_encounters")
    rng = random.Random(config.seed)
    base_count = config.total_encounters - config.stress_encounters
    encounters = [generate_encounter(i, rng, base_count=base_count) for i in range(base_count)]
    encounters.extend(generate_encounter(i, rng, base_count=base_count, stress=True) for i in range(base_count, config.total_encounters))
    return encounters


def write_dataset(output_dir: Path, config: GeneratorConfig = GeneratorConfig()) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    encounters = generate_dataset(config)
    dataset_path = output_dir / "encounters.jsonl"
    with dataset_path.open("w", encoding="utf-8") as handle:
        for encounter in encounters:
            handle.write(encounter.model_dump_json() + "\n")
    splits = {name: 0 for name in ("train", "validation", "test", "stress")}
    trajectories: dict[str, int] = {}
    history = {name.value: 0 for name in HistoryStatus}
    for encounter in encounters:
        splits[encounter.truth.split] += 1
        trajectories[encounter.truth.trajectory_type] = trajectories.get(encounter.truth.trajectory_type, 0) + 1
        history[encounter.patient.history_status.value] += 1
    manifest = {
        "generator_version": GENERATOR_VERSION,
        "seed": config.seed,
        "encounters": len(encounters),
        "file": dataset_path.name,
        "splits": splits,
        "trajectories": trajectories,
        "history_status": history,
        "synthetic_only": True,
        "not_for_clinical_use": True,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
