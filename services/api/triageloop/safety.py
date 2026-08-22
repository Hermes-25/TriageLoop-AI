"""Age-aware deterministic safety gate. Prototype only; not clinical guidance."""

from __future__ import annotations

from datetime import datetime

from .quality import assess_data_quality
from .schemas import (
    AgeBand,
    MentalStatus,
    PatientState,
    RuleHit,
    RuleSeverity,
    SafetyAssessment,
)


MAX_WAIT_MINUTES = {1: 0, 2: 10, 3: 30, 4: 60, 5: 120}
HARD_CUES = {
    "stridor",
    "cyanosis",
    "active seizure",
    "unresponsive",
    "severe respiratory distress",
    "uncontrolled bleeding",
    "stroke signs",
}


def age_band(age_years: float) -> AgeBand:
    if age_years < 12:
        return AgeBand.PEDIATRIC
    if age_years >= 65:
        return AgeBand.GERIATRIC
    return AgeBand.ADULT


def _pediatric_extreme(age: float, hr: float | None, rr: float | None, sbp: float | None) -> list[str]:
    reasons = []
    if age < 1:
        if hr is not None and (hr < 80 or hr > 180):
            reasons.append("age-adjusted extreme heart rate")
        if rr is not None and (rr < 20 or rr > 60):
            reasons.append("age-adjusted extreme respiratory rate")
        if sbp is not None and sbp < 70:
            reasons.append("age-adjusted hypotension")
    elif age < 4:
        if hr is not None and (hr < 70 or hr > 170):
            reasons.append("age-adjusted extreme heart rate")
        if rr is not None and (rr < 15 or rr > 50):
            reasons.append("age-adjusted extreme respiratory rate")
        if sbp is not None and sbp < 70 + 2 * age:
            reasons.append("age-adjusted hypotension")
    elif age < 6:
        if hr is not None and (hr < 60 or hr > 160):
            reasons.append("age-adjusted extreme heart rate")
        if rr is not None and (rr < 15 or rr > 50):
            reasons.append("age-adjusted extreme respiratory rate")
        if sbp is not None and sbp < 70 + 2 * age:
            reasons.append("age-adjusted hypotension")
    else:
        if hr is not None and (hr < 50 or hr > 150):
            reasons.append("age-adjusted extreme heart rate")
        if rr is not None and (rr < 10 or rr > 40):
            reasons.append("age-adjusted extreme respiratory rate")
        if sbp is not None and sbp < (70 + 2 * age if age <= 10 else 90):
            reasons.append("age-adjusted hypotension")
    return reasons


def _trajectory_hits(patient: PatientState) -> list[RuleHit]:
    if len(patient.observations) < 2:
        return []
    prior = patient.observations[-2].values
    latest = patient.observations[-1].values
    changes = []
    if prior.spo2_percent is not None and latest.spo2_percent is not None and prior.spo2_percent - latest.spo2_percent >= 3:
        changes.append("SpO2 fell by at least 3 points")
    if prior.respiratory_rate_per_min is not None and latest.respiratory_rate_per_min is not None and latest.respiratory_rate_per_min - prior.respiratory_rate_per_min >= 5:
        changes.append("respiratory rate rose by at least 5/min")
    if prior.systolic_bp_mmhg is not None and latest.systolic_bp_mmhg is not None and prior.systolic_bp_mmhg - latest.systolic_bp_mmhg >= 15:
        changes.append("systolic pressure fell by at least 15 mmHg")
    if prior.gcs is not None and latest.gcs is not None and prior.gcs - latest.gcs >= 2:
        changes.append("GCS fell by at least 2 points")
    if not changes:
        return []
    return [RuleHit(code="WORSENING_TRAJECTORY", severity=RuleSeverity.URGENT, message="; ".join(changes), recommended_level=2)]


def evaluate_safety(patient: PatientState, *, evaluated_at: datetime | None = None) -> SafetyAssessment:
    latest = patient.observations[-1]
    values = latest.values
    band = age_band(patient.age_years)
    hits: list[RuleHit] = []

    hard_reasons = []
    if values.gcs is not None and values.gcs <= 8:
        hard_reasons.append("GCS at or below 8")
    if values.spo2_percent is not None and values.spo2_percent < 90:
        hard_reasons.append("SpO2 below 90%")
    if values.mental_status in {MentalStatus.PAIN, MentalStatus.UNRESPONSIVE}:
        hard_reasons.append("severely impaired responsiveness")
    if band == AgeBand.PEDIATRIC:
        hard_reasons.extend(_pediatric_extreme(patient.age_years, values.heart_rate_bpm, values.respiratory_rate_per_min, values.systolic_bp_mmhg))
    else:
        if values.respiratory_rate_per_min is not None and (values.respiratory_rate_per_min < 8 or values.respiratory_rate_per_min > 35):
            hard_reasons.append("extreme respiratory rate")
        if values.systolic_bp_mmhg is not None and values.systolic_bp_mmhg < 80:
            hard_reasons.append("severe hypotension")
    cue_text = " ".join(patient.observed_cues).lower()
    matched_cues = sorted(cue for cue in HARD_CUES if cue in cue_text)
    if matched_cues:
        hard_reasons.append("observed hard-red-flag cue: " + ", ".join(matched_cues))
    if hard_reasons:
        hits.append(RuleHit(code="HARD_RED_FLAG", severity=RuleSeverity.HARD, message="; ".join(hard_reasons), recommended_level=1))

    urgent_reasons = []
    if values.spo2_percent is not None and 90 <= values.spo2_percent <= 93:
        urgent_reasons.append("borderline-low SpO2")
    if values.gcs is not None and values.gcs < 15:
        urgent_reasons.append("GCS below 15")
    if values.mental_status == MentalStatus.CONFUSED:
        urgent_reasons.append("new or recorded confusion")
    if values.pain_score_0_10 is not None and values.pain_score_0_10 >= 8:
        urgent_reasons.append("severe reported pain")
    if band == AgeBand.GERIATRIC and patient.history.frailty_score is not None and patient.history.frailty_score >= 7:
        urgent_reasons.append("high geriatric frailty")
    if urgent_reasons:
        hits.append(RuleHit(code="URGENT_REVIEW", severity=RuleSeverity.URGENT, message="; ".join(urgent_reasons), recommended_level=2))
    hits.extend(_trajectory_hits(patient))

    now = evaluated_at or latest.recorded_at
    wait_minutes = max(0.0, (now - patient.arrival_time).total_seconds() / 60)
    max_wait = MAX_WAIT_MINUTES[patient.clinician_state.assigned_level]
    if wait_minutes >= max_wait and patient.clinician_state.assigned_level > 1:
        hits.append(RuleHit(code="WAIT_THRESHOLD", severity=RuleSeverity.REVIEW, message=f"wait of {wait_minutes:.1f} minutes reached the category-{patient.clinician_state.assigned_level} threshold", recommended_level=max(1, patient.clinician_state.assigned_level - 1)))

    quality = assess_data_quality(patient, evaluated_at=now)
    recommended = patient.clinician_state.assigned_level
    for hit in hits:
        recommended = min(recommended, hit.recommended_level)
    rationale = [hit.message for hit in hits]
    if quality.safe_mode:
        rationale.extend(quality.reasons)
    if not rationale:
        rationale.append("no deterministic escalation trigger detected")
    return SafetyAssessment(
        age_band=band,
        rule_hits=hits,
        data_quality=quality,
        clinician_assigned_level=patient.clinician_state.assigned_level,
        recommended_level=recommended,
        reassessment_due=bool(hits) or quality.safe_mode,
        safe_mode=quality.safe_mode,
        rationale=rationale,
    )
