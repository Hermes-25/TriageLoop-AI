"""Model bundle, Dynamic Action Window and Next Best Observation orchestration."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
import json
from pathlib import Path
from typing import Literal
from uuid import uuid4

import numpy as np
from pydantic import Field

from .features import FeatureTransformer, HORIZONS, VITAL_FIELDS, extract_features
from .modeling import BoostedHazard, CalibratedModel, LogisticHazard
from .safety import MAX_WAIT_MINUTES, evaluate_safety
from .schemas import PatientState, StrictModel
from .uncertainty import MondrianConformal, OODDetector


class RecommendedAction(StrEnum):
    IMMEDIATE_REVIEW = "immediate_review"
    REASSESS = "reassess"
    ESCALATE_PRIORITY = "escalate_priority"
    CONTINUE_MONITORED_WAIT = "continue_monitored_wait"
    SAFE_MODE_REVIEW = "safe_mode_review"


class ActionBasis(StrEnum):
    HARD_RULE = "hard_rule"
    CATEGORY_BOUND = "category_bound"
    CALIBRATED_HAZARD = "calibrated_hazard"
    SAFE_MODE = "safe_mode"


class UncertaintyState(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    UNAVAILABLE = "unavailable"


class Burden(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ActionWindow(StrictModel):
    minimum_minutes: float = Field(ge=0)
    maximum_minutes: float = Field(ge=0)
    basis: list[ActionBasis]


class UncertaintyResult(StrictModel):
    state: UncertaintyState
    prediction_set: list[Literal["critical", "non_critical"]]
    abstained: bool
    ood: bool
    data_quality_score: float = Field(ge=0, le=1)


class SafetyEnvelope(StrictModel):
    safe_mode: bool
    safe_mode_reasons: list[str]
    rule_hits: list[str]
    autonomous_downgrade_permitted: Literal[False] = False


class NextBestObservation(StrictModel):
    observation_code: str
    label: str
    recommended_within_minutes: float = Field(ge=0)
    expected_decision_value: float = Field(ge=0, le=1)
    burden: Burden


class Explanation(StrictModel):
    summary: str
    what_changed: list[str]
    top_factors: list[str]


class RecommendationEnvelope(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    recommendation_id: str
    patient_id: str = Field(pattern=r"^P-[0-9]{3,6}$")
    generated_at: datetime
    recommended_action: RecommendedAction
    action_window: ActionWindow
    predicted_time_to_action_minutes: float | None = Field(default=None, ge=0)
    clinical_slack_minutes: float | None = None
    capacity_conflict: bool = False
    risk_by_horizon: dict[str, float]
    uncertainty: UncertaintyResult
    safety: SafetyEnvelope
    next_best_observation: NextBestObservation | None = None
    explanation: Explanation
    component_versions: dict[str, str]


OBSERVATION_LABELS = {
    "heart_rate_bpm": ("repeat_heart_rate", "Repeat heart rate"),
    "respiratory_rate_per_min": ("repeat_respiratory_rate", "Repeat respiratory rate"),
    "spo2_percent": ("repeat_spo2", "Repeat SpO2"),
    "systolic_bp_mmhg": ("repeat_blood_pressure", "Repeat blood pressure"),
    "diastolic_bp_mmhg": ("repeat_blood_pressure", "Repeat blood pressure"),
    "temperature_c": ("repeat_temperature", "Repeat temperature"),
    "gcs": ("repeat_mental_status", "Repeat mental-status/GCS check"),
    "pain_score_0_10": ("repeat_pain", "Repeat pain assessment"),
}


FACTOR_LABELS = {
    "age_years": ("age", "years"),
    "frailty_score": ("frailty score", ""),
    "assigned_level": ("clinician-assigned triage level", ""),
    "elapsed_minutes": ("elapsed waiting time", "minutes"),
    "quality_completeness": ("observation completeness", ""),
    "quality_reliability": ("observation reliability", ""),
    "current_heart_rate_bpm": ("heart rate", "bpm"),
    "current_respiratory_rate_per_min": ("respiratory rate", "/min"),
    "current_spo2_percent": ("oxygen saturation", "%"),
    "current_systolic_bp_mmhg": ("systolic blood pressure", "mmHg"),
    "current_diastolic_bp_mmhg": ("diastolic blood pressure", "mmHg"),
    "current_temperature_c": ("temperature", "°C"),
    "current_gcs": ("GCS", ""),
    "current_pain_score_0_10": ("pain score", "/10"),
    "delta_heart_rate_bpm": ("heart-rate trend", "bpm"),
    "delta_respiratory_rate_per_min": ("respiratory-rate trend", "/min"),
    "delta_spo2_percent": ("oxygen-saturation trend", "points"),
    "delta_systolic_bp_mmhg": ("systolic-pressure trend", "mmHg"),
    "delta_diastolic_bp_mmhg": ("diastolic-pressure trend", "mmHg"),
    "delta_temperature_c": ("temperature trend", "°C"),
    "delta_gcs": ("GCS trend", "points"),
    "delta_pain_score_0_10": ("pain-score trend", "points"),
}

BINARY_FACTOR_LABELS = {
    "is_pediatric": "paediatric age band",
    "is_geriatric": "geriatric age band",
    "history_partial": "partially available history",
    "history_available": "available clinical history",
    "text_respiratory": "reported respiratory symptoms",
    "text_chest": "reported chest symptoms",
    "text_neuro": "reported neurological symptoms",
    "text_fever": "reported fever or sepsis symptoms",
    "text_abdominal": "reported abdominal symptoms",
    "text_trauma": "reported trauma symptoms",
    "mental_confused": "observed confusion",
    "mental_impaired": "impaired responsiveness",
}


class ModelBundle:
    def __init__(self, payload: dict[str, object]):
        self.version = str(payload["model_version"])
        self.family = str(payload["family"])
        self.transformer = FeatureTransformer.from_dict(payload["transformer"])
        self.model = CalibratedModel.from_dict(payload["calibrated_model"])
        self.thresholds = np.asarray([payload["thresholds"][str(horizon)] for horizon in HORIZONS], dtype=float)
        self.conformal = MondrianConformal(alpha=float(payload["conformal"]["alpha"]), thresholds=payload["conformal"]["thresholds"])
        self.ood = OODDetector(quantile=float(payload["ood"]["quantile"]), threshold=float(payload["ood"]["threshold"]))

    @classmethod
    def from_path(cls, path: Path) -> "ModelBundle":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def predict(self, patient: PatientState) -> tuple[np.ndarray, list[list[str]], bool, np.ndarray]:
        raw = extract_features(patient).reshape(1, -1)
        transformed = self.transformer.transform(raw)
        probability = self.model.predict_proba(transformed)[0]
        prediction_sets = self.conformal.prediction_sets(probability.reshape(1, -1))[0]
        return probability, prediction_sets, bool(self.ood.predict(transformed)[0]), transformed[0]

    def local_factors(
        self,
        transformed: np.ndarray,
        raw_features: np.ndarray,
        horizon_index: int = 2,
        count: int = 5,
    ) -> list[str]:
        """Return observed, positive urgency drivers in nurse-readable language.

        Centered model features can assign a contribution to the *absence* of a
        binary finding. That is mathematically valid but unsafe to verbalize as
        if the finding were observed (for example, "confused reduced urgency").
        The product therefore shows only positive drivers grounded in the
        patient's recorded values. The model score itself is unchanged.
        """
        estimator = self.model.model.models[horizon_index]
        contributions = np.zeros(len(transformed))
        if isinstance(estimator, LogisticHazard):
            contributions = estimator.weights[1:] * transformed
        elif isinstance(estimator, BoostedHazard):
            for tree in estimator.trees:
                value = tree.left_value if transformed[tree.feature] <= tree.threshold else tree.right_value
                contributions[tree.feature] += estimator.learning_rate * value
        order = np.argsort(np.abs(contributions))[::-1]
        factors = []
        for index in order:
            if contributions[index] <= 1e-8:
                continue
            name = self.transformer.names[index]
            raw_value = float(raw_features[index])
            if np.isnan(raw_value):
                continue
            if name in BINARY_FACTOR_LABELS:
                if raw_value < 0.5:
                    continue
                factors.append(f"{BINARY_FACTOR_LABELS[name]} increased estimated urgency")
            elif name.startswith("missing_"):
                if raw_value < 0.5:
                    continue
                missing_name = name.removeprefix("missing_").replace("_", " ")
                factors.append(f"missing {missing_name} increased estimated urgency")
            elif name in FACTOR_LABELS:
                if name.startswith("delta_") and abs(raw_value) < 0.01:
                    continue
                label, unit = FACTOR_LABELS[name]
                value = f"{raw_value:+g}" if name.startswith("delta_") else f"{raw_value:g}"
                spacer = " " if unit and not unit.startswith(("/", "%")) else ""
                factors.append(f"{label} ({value}{spacer}{unit}) increased estimated urgency")
            else:
                factors.append(f"{name.replace('_', ' ')} increased estimated urgency")
            if len(factors) == count:
                break
        return factors or ["no single observed model driver dominated; rules and category bounds govern the action"]

    def observation_importance(self, horizon_index: int = 2) -> np.ndarray:
        return self.model.model.models[horizon_index].feature_importance()


def _what_changed(patient: PatientState) -> list[str]:
    if len(patient.observations) < 2:
        return ["first recorded observation"]
    prior, current = patient.observations[-2].values, patient.observations[-1].values
    changes = []
    for field in VITAL_FIELDS:
        before, after = getattr(prior, field), getattr(current, field)
        if before is not None and after is not None and abs(after - before) > 0.01:
            direction = "rose" if after > before else "fell"
            changes.append(f"{field} {direction} from {before:g} to {after:g}")
    return changes[:5] or ["no material numeric change since the prior observation"]


def rank_observation_options(
    patient: PatientState,
    bundle: ModelBundle,
    probability: np.ndarray,
    action_minutes: float,
    quality_fields: set[str],
) -> list[NextBestObservation]:
    importance = bundle.observation_importance(2)
    names = bundle.transformer.names
    latest = patient.observations[-1].values
    uncertainty = 1 - min(1.0, abs(probability[2] - bundle.thresholds[2]) * 4)
    candidates: dict[str, tuple[str, str, float]] = {}
    for vital in VITAL_FIELDS:
        code, label = OBSERVATION_LABELS[vital]
        related = sum(float(importance[index]) for index, name in enumerate(names) if vital in name)
        quality_bonus = 1.0 if vital in quality_fields or ("blood_pressure_relation" in quality_fields and "bp_mmhg" in vital) else 0.0
        score = min(1.0, 0.15 + 0.55 * uncertainty + 0.25 * min(1.0, related) + 0.4 * quality_bonus)
        previous = candidates.get(code)
        if previous is None or score > previous[2]:
            candidates[code] = (code, label, score)
    return [
        NextBestObservation(
            observation_code=code,
            label=label,
            recommended_within_minutes=min(10.0, action_minutes),
            expected_decision_value=round(score, 3),
            burden=Burden.LOW,
        )
        for code, label, score in sorted(candidates.values(), key=lambda item: (-item[2], item[0]))
    ]


def _next_best_observation(
    patient: PatientState,
    bundle: ModelBundle,
    probability: np.ndarray,
    action_minutes: float,
    quality_fields: set[str],
) -> NextBestObservation:
    return rank_observation_options(patient, bundle, probability, action_minutes, quality_fields)[0]


def recommend(patient: PatientState, bundle: ModelBundle, *, evaluated_at: datetime | None = None) -> RecommendationEnvelope:
    now = evaluated_at or patient.observations[-1].recorded_at
    safety = evaluate_safety(patient, evaluated_at=now)
    probability, prediction_sets, ood, transformed = bundle.predict(patient)
    raw_features = extract_features(patient)
    elapsed = max(0.0, (now - patient.arrival_time).total_seconds() / 60)
    category_remaining = max(0.0, MAX_WAIT_MINUTES[patient.clinician_state.assigned_level] - elapsed)
    hard_rule = any(hit.severity.value == "hard" for hit in safety.rule_hits)
    decision_set = prediction_sets[2]
    ambiguous = len(decision_set) != 1 and not hard_rule
    material_ambiguity = len(prediction_sets[1]) != 1 and probability[1] >= bundle.thresholds[1] * 0.5 and not hard_rule
    safe_mode = safety.safe_mode or ood or material_ambiguity
    reasons = list(safety.data_quality.reasons)
    if ood:
        reasons.append("feature state is outside the registered training envelope")
    if material_ambiguity:
        reasons.append("near-term conformal prediction set is materially ambiguous")

    hazard_horizon = next((horizon for index, horizon in enumerate(HORIZONS) if probability[index] >= bundle.thresholds[index]), None)
    basis = [ActionBasis.CATEGORY_BOUND]
    maximum = category_remaining
    if hazard_horizon is not None:
        maximum = min(maximum, float(hazard_horizon))
        basis.append(ActionBasis.CALIBRATED_HAZARD)
    if hard_rule:
        maximum = 0.0
        basis.append(ActionBasis.HARD_RULE)
    elif safe_mode:
        maximum = min(maximum, 5.0)
        basis.append(ActionBasis.SAFE_MODE)

    if hard_rule:
        action = RecommendedAction.IMMEDIATE_REVIEW
    elif safe_mode:
        action = RecommendedAction.SAFE_MODE_REVIEW
    elif safety.recommended_level < patient.clinician_state.assigned_level:
        action = RecommendedAction.ESCALATE_PRIORITY
    elif maximum <= 10:
        action = RecommendedAction.REASSESS
    else:
        action = RecommendedAction.CONTINUE_MONITORED_WAIT

    if safe_mode or ambiguous:
        uncertainty_state = UncertaintyState.HIGH
    elif abs(probability[2] - bundle.thresholds[2]) < 0.08:
        uncertainty_state = UncertaintyState.MODERATE
    else:
        uncertainty_state = UncertaintyState.LOW
    needs_observation = (safe_mode or ambiguous or uncertainty_state == UncertaintyState.MODERATE) and not hard_rule
    quality_fields = set(safety.data_quality.missing_fields + safety.data_quality.implausible_fields)
    nbo = _next_best_observation(patient, bundle, probability, maximum, quality_fields) if needs_observation else None
    summary = f"{action.value.replace('_', ' ').title()}; recommended within {maximum:.0f} minutes."
    return RecommendationEnvelope(
        recommendation_id=f"REC-{uuid4().hex[:12]}",
        patient_id=patient.patient_id,
        generated_at=now,
        recommended_action=action,
        action_window=ActionWindow(minimum_minutes=0, maximum_minutes=maximum, basis=list(dict.fromkeys(basis))),
        risk_by_horizon={str(horizon): round(float(probability[index]), 6) for index, horizon in enumerate(HORIZONS)},
        uncertainty=UncertaintyResult(
            state=uncertainty_state,
            prediction_set=decision_set,
            abstained=safe_mode,
            ood=ood,
            data_quality_score=safety.data_quality.reliability,
        ),
        safety=SafetyEnvelope(
            safe_mode=safe_mode,
            safe_mode_reasons=reasons,
            rule_hits=[hit.code for hit in safety.rule_hits],
        ),
        next_best_observation=nbo,
        explanation=Explanation(
            summary=summary,
            what_changed=_what_changed(patient),
            top_factors=bundle.local_factors(transformed, raw_features),
        ),
        component_versions={"model": bundle.version, "rules": "1.0.0", "features": "1.0.0", "contract": "1.0.0"},
    )
