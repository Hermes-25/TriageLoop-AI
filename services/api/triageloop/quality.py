"""Deterministic input-quality checks used before any future model call."""

from __future__ import annotations

from datetime import datetime, timezone

from .schemas import DataQualityAssessment, PatientState, QualityFlag


CORE_FIELDS = (
    "heart_rate_bpm",
    "respiratory_rate_per_min",
    "spo2_percent",
    "systolic_bp_mmhg",
    "temperature_c",
)

PLAUSIBLE_RANGES: dict[str, tuple[float, float]] = {
    "heart_rate_bpm": (15, 300),
    "respiratory_rate_per_min": (2, 100),
    "spo2_percent": (40, 100),
    "systolic_bp_mmhg": (30, 300),
    "diastolic_bp_mmhg": (15, 200),
    "temperature_c": (25, 45),
    "gcs": (3, 15),
    "pain_score_0_10": (0, 10),
}


def assess_data_quality(
    patient: PatientState,
    *,
    evaluated_at: datetime | None = None,
    stale_after_minutes: float = 30,
) -> DataQualityAssessment:
    latest = patient.observations[-1]
    now = evaluated_at or latest.recorded_at
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    stale_minutes = max(0.0, (now - latest.recorded_at).total_seconds() / 60)

    values = latest.values
    missing = [name for name in CORE_FIELDS if getattr(values, name) is None]
    implausible = []
    populated = 0
    fields = list(PLAUSIBLE_RANGES)
    for name, (lower, upper) in PLAUSIBLE_RANGES.items():
        value = getattr(values, name)
        if value is None:
            continue
        populated += 1
        if not lower <= value <= upper:
            implausible.append(name)
    if (
        values.systolic_bp_mmhg is not None
        and values.diastolic_bp_mmhg is not None
        and values.diastolic_bp_mmhg >= values.systolic_bp_mmhg
    ):
        implausible.append("blood_pressure_relation")

    flags = list(dict.fromkeys(latest.quality.flags))
    if missing and QualityFlag.MISSING not in flags:
        flags.append(QualityFlag.MISSING)
    if implausible and QualityFlag.IMPLAUSIBLE not in flags:
        flags.append(QualityFlag.IMPLAUSIBLE)
    if stale_minutes > stale_after_minutes and QualityFlag.STALE not in flags:
        flags.append(QualityFlag.STALE)

    completeness = populated / len(fields)
    reliability = min(latest.quality.reliability, 1 - 0.1 * len(missing) - 0.25 * len(implausible))
    reliability = max(0.0, reliability)
    reasons = []
    if missing:
        reasons.append("critical observations missing: " + ", ".join(missing))
    if implausible:
        reasons.append("implausible or inconsistent values: " + ", ".join(implausible))
    if stale_minutes > stale_after_minutes:
        reasons.append(f"latest observation is {stale_minutes:.1f} minutes old")

    return DataQualityAssessment(
        completeness=round(completeness, 4),
        reliability=round(reliability, 4),
        missing_fields=missing,
        implausible_fields=implausible,
        stale_minutes=round(stale_minutes, 2),
        flags=flags,
        safe_mode=bool(reasons),
        reasons=reasons,
    )
