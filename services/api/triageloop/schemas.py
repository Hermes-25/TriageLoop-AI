"""Runtime contracts for synthetic patient trajectories and safety outputs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SexAtBirth(StrEnum):
    FEMALE = "female"
    MALE = "male"
    INTERSEX = "intersex"
    UNKNOWN = "unknown"


class PregnancyStatus(StrEnum):
    PREGNANT = "pregnant"
    NOT_PREGNANT = "not_pregnant"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class HistoryStatus(StrEnum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    NONE = "none"


class MentalStatus(StrEnum):
    ALERT = "alert"
    VOICE = "voice"
    PAIN = "pain"
    UNRESPONSIVE = "unresponsive"
    CONFUSED = "confused"
    UNKNOWN = "unknown"


class ObservationSource(StrEnum):
    TRIAGE = "triage"
    REASSESSMENT = "reassessment"
    MONITOR = "monitor"
    MANUAL_CORRECTION = "manual_correction"
    SYNTHETIC_EVENT = "synthetic_event"


class QualityFlag(StrEnum):
    MISSING = "missing"
    STALE = "stale"
    IMPLAUSIBLE = "implausible"
    CORRECTED = "corrected"
    DEVICE_WARNING = "device_warning"
    SELF_REPORTED = "self_reported"


class ClinicianStatus(StrEnum):
    WAITING = "waiting"
    REASSESSMENT_DUE = "reassessment_due"
    ESCALATED = "escalated"
    IN_CARE = "in_care"
    COMPLETED = "completed"


class ActorRole(StrEnum):
    NURSE = "nurse"
    CHARGE_NURSE = "charge_nurse"
    CLINICIAN = "clinician"
    SYSTEM_FIXTURE = "system_fixture"


class ProvenanceSource(StrEnum):
    MANUAL = "manual"
    CSV = "csv"
    FHIR_LIKE = "fhir_like"
    SYNTHETIC_GENERATOR = "synthetic_generator"
    SCRIPTED_FIXTURE = "scripted_fixture"


class AgeBand(StrEnum):
    PEDIATRIC = "pediatric"
    ADULT = "adult"
    GERIATRIC = "geriatric"


class RuleSeverity(StrEnum):
    HARD = "hard"
    URGENT = "urgent"
    REVIEW = "review"


class VitalValues(StrictModel):
    heart_rate_bpm: float | None = None
    respiratory_rate_per_min: float | None = None
    spo2_percent: float | None = None
    systolic_bp_mmhg: float | None = None
    diastolic_bp_mmhg: float | None = None
    temperature_c: float | None = None
    gcs: float | None = Field(default=None, ge=3, le=15)
    pain_score_0_10: float | None = Field(default=None, ge=0, le=10)
    mental_status: MentalStatus | None = None


class ObservationQuality(StrictModel):
    completeness: float = Field(default=1.0, ge=0, le=1)
    reliability: float = Field(default=1.0, ge=0, le=1)
    flags: list[QualityFlag] = Field(default_factory=list)


class Observation(StrictModel):
    observation_id: str = Field(min_length=1, max_length=64)
    recorded_at: datetime
    source: ObservationSource
    values: VitalValues
    quality: ObservationQuality = Field(default_factory=ObservationQuality)


class MedicalHistory(StrictModel):
    conditions: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    frailty_score: int | None = Field(default=None, ge=1, le=9)


class ClinicianState(StrictModel):
    assigned_level: int = Field(ge=1, le=5)
    status: ClinicianStatus = ClinicianStatus.WAITING
    assigned_by_role: ActorRole = ActorRole.NURSE


class Provenance(StrictModel):
    source: ProvenanceSource
    synthetic: Literal[True] = True
    generator_version: str | None = None
    scenario_id: str | None = None


class PatientState(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    patient_id: str = Field(pattern=r"^P-[0-9]{3,6}$")
    arrival_time: datetime
    age_years: float = Field(ge=0, le=120)
    sex_at_birth: SexAtBirth
    pregnancy_status: PregnancyStatus | None = None
    chief_complaint: str = Field(min_length=1, max_length=500)
    reported_symptoms: list[str] = Field(default_factory=list)
    observed_cues: list[str] = Field(default_factory=list)
    history_status: HistoryStatus
    history: MedicalHistory = Field(default_factory=MedicalHistory)
    observations: list[Observation] = Field(min_length=1)
    clinician_state: ClinicianState
    provenance: Provenance

    @model_validator(mode="after")
    def validate_trajectory(self) -> "PatientState":
        timestamps = [item.recorded_at for item in self.observations]
        if timestamps != sorted(timestamps):
            raise ValueError("observations must be in chronological order")
        if timestamps[0] < self.arrival_time:
            raise ValueError("an observation cannot predate arrival")
        if self.history_status == HistoryStatus.NONE and (
            self.history.conditions
            or self.history.medications
            or self.history.allergies
            or self.history.frailty_score is not None
        ):
            raise ValueError("history_status=none cannot contain prior-record fields")
        return self


class RuleHit(StrictModel):
    code: str
    severity: RuleSeverity
    message: str
    recommended_level: int = Field(ge=1, le=5)


class DataQualityAssessment(StrictModel):
    completeness: float = Field(ge=0, le=1)
    reliability: float = Field(ge=0, le=1)
    missing_fields: list[str] = Field(default_factory=list)
    implausible_fields: list[str] = Field(default_factory=list)
    stale_minutes: float = Field(ge=0)
    flags: list[QualityFlag] = Field(default_factory=list)
    safe_mode: bool
    reasons: list[str] = Field(default_factory=list)


class SafetyAssessment(StrictModel):
    age_band: AgeBand
    rule_hits: list[RuleHit]
    data_quality: DataQualityAssessment
    clinician_assigned_level: int = Field(ge=1, le=5)
    recommended_level: int = Field(ge=1, le=5)
    autonomous_downgrade: Literal[False] = False
    reassessment_due: bool
    safe_mode: bool
    rationale: list[str]


class SyntheticTruth(StrictModel):
    trajectory_type: str
    critical_within_5m: bool
    critical_within_15m: bool
    critical_within_30m: bool
    critical_within_60m: bool
    minimum_level: int = Field(ge=1, le=5)
    split: Literal["train", "validation", "test", "stress"]


class SyntheticEncounter(StrictModel):
    encounter_id: str = Field(pattern=r"^E-[0-9]{5,8}$")
    patient: PatientState
    truth: SyntheticTruth
    tags: list[str] = Field(default_factory=list)
