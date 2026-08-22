"""Leakage-safe longitudinal feature extraction for TL-02."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import numpy as np

from .schemas import HistoryStatus, MentalStatus, PatientState, SyntheticEncounter


HORIZONS = (5, 15, 30, 60)
VITAL_FIELDS = (
    "heart_rate_bpm",
    "respiratory_rate_per_min",
    "spo2_percent",
    "systolic_bp_mmhg",
    "diastolic_bp_mmhg",
    "temperature_c",
    "gcs",
    "pain_score_0_10",
)
TEXT_CUES = {
    "text_respiratory": ("breath", "cough", "stridor"),
    "text_chest": ("chest", "palpitation"),
    "text_neuro": ("headache", "dizz", "confus", "stroke", "collapse"),
    "text_fever": ("fever", "sepsis"),
    "text_abdominal": ("abdominal", "vomit"),
    "text_trauma": ("fall", "laceration", "bleeding", "injury"),
}


def feature_names() -> list[str]:
    names = [
        "age_years",
        "is_pediatric",
        "is_geriatric",
        "sex_female",
        "history_partial",
        "history_available",
        "condition_count",
        "frailty_score",
        "assigned_level",
        "elapsed_minutes",
        "quality_completeness",
        "quality_reliability",
    ]
    names.extend(f"current_{field}" for field in VITAL_FIELDS)
    names.extend(f"missing_{field}" for field in VITAL_FIELDS)
    names.extend(f"delta_{field}" for field in VITAL_FIELDS)
    names.extend(TEXT_CUES)
    names.extend(("mental_confused", "mental_impaired"))
    return names


def _number(value: float | None) -> float:
    return np.nan if value is None else float(value)


def extract_features(patient: PatientState, observation_index: int | None = None) -> np.ndarray:
    index = len(patient.observations) - 1 if observation_index is None else observation_index
    current_observation = patient.observations[index]
    current = current_observation.values
    prior = patient.observations[index - 1].values if index > 0 else None
    elapsed = (current_observation.recorded_at - patient.arrival_time).total_seconds() / 60
    values: list[float] = [
        patient.age_years,
        float(patient.age_years < 12),
        float(patient.age_years >= 65),
        float(patient.sex_at_birth.value == "female"),
        float(patient.history_status == HistoryStatus.PARTIAL),
        float(patient.history_status == HistoryStatus.AVAILABLE),
        float(len(patient.history.conditions)),
        float(patient.history.frailty_score or 0),
        float(patient.clinician_state.assigned_level),
        elapsed,
        current_observation.quality.completeness,
        current_observation.quality.reliability,
    ]
    values.extend(_number(getattr(current, field)) for field in VITAL_FIELDS)
    values.extend(float(getattr(current, field) is None) for field in VITAL_FIELDS)
    for field in VITAL_FIELDS:
        current_value = getattr(current, field)
        prior_value = getattr(prior, field) if prior is not None else None
        values.append(_number(current_value - prior_value) if current_value is not None and prior_value is not None else np.nan)
    text = " ".join((patient.chief_complaint, *patient.reported_symptoms, *patient.observed_cues)).lower()
    values.extend(float(any(token in text for token in tokens)) for tokens in TEXT_CUES.values())
    values.extend(
        (
            float(current.mental_status == MentalStatus.CONFUSED),
            float(current.mental_status in {MentalStatus.VOICE, MentalStatus.PAIN, MentalStatus.UNRESPONSIVE}),
        )
    )
    return np.asarray(values, dtype=float)


def event_minute(encounter: SyntheticEncounter) -> int | None:
    truth = encounter.truth
    if truth.critical_within_5m:
        return 5
    if truth.critical_within_15m:
        return 15
    if truth.critical_within_30m:
        return 30
    if truth.critical_within_60m:
        return 60
    return None


def snapshot_rows(encounter: SyntheticEncounter) -> Iterator[tuple[np.ndarray, np.ndarray, dict[str, object]]]:
    event = event_minute(encounter)
    for index, observation in enumerate(encounter.patient.observations):
        elapsed = (observation.recorded_at - encounter.patient.arrival_time).total_seconds() / 60
        labels = np.asarray(
            [float(event is not None and event <= elapsed + horizon) for horizon in HORIZONS],
            dtype=float,
        )
        yield extract_features(encounter.patient, index), labels, {
            "encounter_id": encounter.encounter_id,
            "patient_id": encounter.patient.patient_id,
            "split": encounter.truth.split,
            "age_group": "pediatric" if encounter.patient.age_years < 12 else "geriatric" if encounter.patient.age_years >= 65 else "adult",
            "history_status": encounter.patient.history_status.value,
            "elapsed_minutes": elapsed,
            "trajectory_type": encounter.truth.trajectory_type,
        }


def load_encounters(path: Path) -> Iterator[SyntheticEncounter]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            yield SyntheticEncounter.model_validate_json(line)


def build_snapshot_dataset(encounters: Iterable[SyntheticEncounter]) -> dict[str, tuple[np.ndarray, np.ndarray, list[dict[str, object]]]]:
    buckets: dict[str, list[tuple[np.ndarray, np.ndarray, dict[str, object]]]] = {
        "train": [],
        "validation": [],
        "test": [],
        "stress": [],
    }
    for encounter in encounters:
        buckets[encounter.truth.split].extend(snapshot_rows(encounter))
    result = {}
    width = len(feature_names())
    for split, rows in buckets.items():
        if rows:
            x = np.vstack([row[0] for row in rows])
            y = np.vstack([row[1] for row in rows])
            metadata = [row[2] for row in rows]
        else:
            x, y, metadata = np.empty((0, width)), np.empty((0, len(HORIZONS))), []
        result[split] = (x, y, metadata)
    return result


@dataclass
class FeatureTransformer:
    names: list[str]
    medians: np.ndarray | None = None
    means: np.ndarray | None = None
    scales: np.ndarray | None = None

    @classmethod
    def create(cls) -> "FeatureTransformer":
        return cls(names=feature_names())

    def fit(self, x: np.ndarray) -> "FeatureTransformer":
        self.medians = np.nanmedian(x, axis=0)
        self.medians = np.where(np.isnan(self.medians), 0.0, self.medians)
        imputed = np.where(np.isnan(x), self.medians, x)
        self.means = imputed.mean(axis=0)
        self.scales = imputed.std(axis=0)
        self.scales = np.where(self.scales < 1e-8, 1.0, self.scales)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.medians is None or self.means is None or self.scales is None:
            raise RuntimeError("feature transformer is not fitted")
        imputed = np.where(np.isnan(x), self.medians, x)
        return (imputed - self.means) / self.scales

    def to_dict(self) -> dict[str, object]:
        return {
            "names": self.names,
            "medians": self.medians.tolist(),
            "means": self.means.tolist(),
            "scales": self.scales.tolist(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "FeatureTransformer":
        return cls(
            names=list(payload["names"]),
            medians=np.asarray(payload["medians"], dtype=float),
            means=np.asarray(payload["means"], dtype=float),
            scales=np.asarray(payload["scales"], dtype=float),
        )
