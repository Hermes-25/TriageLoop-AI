export type Scenario = "baseline" | "surge_3x";

export interface ObservationValues {
  heart_rate_bpm: number | null;
  respiratory_rate_per_min: number | null;
  spo2_percent: number | null;
  systolic_bp_mmhg: number | null;
  diastolic_bp_mmhg: number | null;
  temperature_c: number | null;
  gcs: number | null;
  pain_score_0_10: number | null;
  mental_status: string | null;
}

export interface Observation {
  observation_id: string;
  recorded_at: string;
  source: string;
  values: ObservationValues;
  quality: { completeness: number; reliability: number; flags: string[] };
}

export interface Recommendation {
  recommendation_id: string;
  patient_id: string;
  generated_at: string;
  recommended_action: string;
  action_window: { minimum_minutes: number; maximum_minutes: number; basis: string[] };
  predicted_time_to_action_minutes: number | null;
  clinical_slack_minutes: number | null;
  capacity_conflict: boolean;
  risk_by_horizon: Record<string, number>;
  uncertainty: {
    state: "low" | "moderate" | "high" | "unavailable";
    prediction_set: string[];
    abstained: boolean;
    ood: boolean;
    data_quality_score: number;
  };
  safety: {
    safe_mode: boolean;
    safe_mode_reasons: string[];
    rule_hits: string[];
    autonomous_downgrade_permitted: false;
  };
  next_best_observation: null | {
    observation_code: string;
    label: string;
    recommended_within_minutes: number;
    expected_decision_value: number;
    burden: string;
  };
  explanation: { summary: string; what_changed: string[]; top_factors: string[] };
  component_versions: Record<string, string>;
}

export interface AuditEvent {
  sequence: number;
  event_id: string;
  patient_id: string | null;
  created_at: string;
  actor: string;
  event_type: string;
  payload: Record<string, unknown>;
  previous_hash: string | null;
  event_hash: string;
}

export interface AuditIntegrity {
  intact: boolean;
  events_checked: number;
  first_broken_sequence: number | null;
  algorithm: string;
  prototype_only: boolean;
}

export interface Patient {
  patient_id: string;
  queue_position: number;
  decision_state: string | null;
  age_years: number;
  age_band: string;
  sex_at_birth: string;
  chief_complaint: string;
  reported_symptoms: string[];
  observed_cues: string[];
  history_status: string;
  history: { conditions: string[]; medications: string[]; allergies: string[]; frailty_score: number | null };
  clinician_level: number;
  wait_minutes: number;
  latest_observation: Observation;
  prior_observation: Observation | null;
  trajectory: number[];
  recommendation: Recommendation;
  updated_at: string;
  audit?: AuditEvent[];
}

export interface ProductState {
  schema_version: string;
  generated_at: string;
  site: string;
  scenario: Scenario;
  scenario_label: string;
  connection: string;
  patients: Patient[];
  summary: { waiting: number; capacity_conflicts: number; safe_mode: number; reassessment_due: number };
  capacity: {
    state: "available" | "constrained";
    clinician_utilization: number;
    reassessment_utilization: number;
    message: string;
  };
  deterioration_applied: boolean;
  prototype_notice: string;
}

export interface Evaluation {
  base_seed: number;
  overall_surge: Record<string, {
    static_mean: number;
    triageloop_mean: number;
    relative_improvement: number;
    ci95_low: number;
    ci95_high: number;
  }>;
  deterioration_response_sensitivity: Record<string, {
    static_mean: number;
    triageloop_mean: number;
    relative_improvement: number;
    ci95_low: number;
    ci95_high: number;
  }>;
  alert_workload: Record<string, Record<string, {
    reassessment_nurses: number;
    mean_consolidated_alerts_per_8h_shift: number;
    mean_alerts_per_waiting_patient_hour: number;
    mean_alerts_per_reassessment_nurse_hour: number;
  }>>;
  site_results: Record<string, { static: Record<string, number>; triageloop: Record<string, number> }>;
  site_comparisons: Record<string, {
    static_mean: number;
    triageloop_mean: number;
    relative_improvement: number;
    ci95_low: number;
    ci95_high: number;
  }>;
  gates: Record<string, boolean>;
  replications: number;
  verification_policy_shifts: number;
  periodic_retriage: {
    minutes: number;
    overall_surge: Evaluation["overall_surge"];
    site_comparisons: Evaluation["site_comparisons"];
    notice: string;
    response_sensitivity: Record<string, {
      periodic_retriage_mean: number;
      triageloop_mean: number;
      relative_improvement: number;
      ci95_low: number;
      ci95_high: number;
      paired_policy_shifts: number;
    }>;
    sensitivity_notice: string;
  };
  nbo_verification: {
    eligible_snapshots: number;
    fixed_bundle: { observations_per_reassessment: number; operational_critical_recall: number };
    next_best_observation: { observations_per_reassessment: number; operational_critical_recall: number };
    comparison: { observation_count_reduction: number; operational_recall_difference_nbo_minus_fixed: number };
    gates: Record<string, boolean>;
    fallback: { status: string; selected_observation_count_on_test: number | null; stress_confirmation_passed: boolean };
  };
  external_plausibility: {
    source: { name: string; version: string; population: string };
    coverage: { mapped_fields: number; mapped_core_fields: number; external_measurements: number };
    checks: Record<string, boolean>;
    not_clinical_validation: boolean;
  };
  synthetic_simulation_only: boolean;
  not_for_clinical_or_staffing_use: boolean;
}
