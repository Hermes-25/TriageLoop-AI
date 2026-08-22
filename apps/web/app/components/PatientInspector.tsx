"use client";

import { Activity, ArrowDown, ArrowLeft, ArrowUp, Clock3, Database, ShieldAlert, Stethoscope } from "lucide-react";
import { DecisionPanel } from "@/app/components/DecisionPanel";
import { formatAction, formatActionWindow, formatEta, RiskSparkline, SlackLine, StatusMark } from "@/app/components/ClinicalVisuals";
import type { ObservationValues, Patient } from "@/app/lib/types";

function vitalDelta(current: number | null, prior: number | null) {
  if (current == null || prior == null || current === prior) return null;
  return current > prior ? <ArrowUp size={12} aria-label="increased" /> : <ArrowDown size={12} aria-label="decreased" />;
}

function Vital({ label, value, suffix, prior }: { label: string; value: number | null; suffix: string; prior: number | null }) {
  return (
    <div className="vital-item">
      <span>{label}</span>
      <strong>{value == null ? "—" : value}<small>{value == null ? "" : suffix}</small>{vitalDelta(value, prior)}</strong>
    </div>
  );
}

export function PatientInspector({ patient, degraded, onClose }: { patient: Patient; degraded: boolean; onClose: () => void }) {
  const rec = patient.recommendation;
  const current = patient.latest_observation.values;
  const prior: ObservationValues = patient.prior_observation?.values ?? {
    heart_rate_bpm: null, respiratory_rate_per_min: null, spo2_percent: null,
    systolic_bp_mmhg: null, diastolic_bp_mmhg: null, temperature_c: null,
    gcs: null, pain_score_0_10: null, mental_status: null,
  };
  const actionKind = rec.safety.safe_mode ? "warning" : rec.capacity_conflict || rec.recommended_action === "immediate_review" ? "critical" : "info";

  return (
    <aside className="patient-inspector" aria-label={`Selected patient ${patient.patient_id}`}>
      <div className="inspector-scroll">
        <button className="inspector-back" type="button" onClick={onClose}><ArrowLeft size={15} aria-hidden="true" /> Back to live queue</button>
        <header className="patient-heading">
          <div>
            <div className="patient-id-line">
              <span className={`level-disc level-${patient.clinician_level}`}>{patient.clinician_level}</span>
              <strong>{patient.patient_id}</strong>
              <span>{patient.age_years}y · {patient.sex_at_birth}</span>
            </div>
            <h2>{patient.chief_complaint}</h2>
          </div>
          <span className="wait-chip"><Clock3 size={13} aria-hidden="true" /> {patient.wait_minutes}m waiting</span>
        </header>

        <section className="recommendation-block" aria-labelledby="action-heading">
          <div className="recommendation-title">
            <div>
              <span id="action-heading">{degraded ? "Last verified action" : "Recommended action"}</span>
              <h3>{formatAction(rec.recommended_action)}</h3>
            </div>
            <StatusMark kind={degraded ? "warning" : actionKind} label={degraded ? "Rules fallback" : rec.safety.safe_mode ? "Safe Mode" : rec.capacity_conflict ? "Capacity conflict" : `${rec.uncertainty.state} uncertainty`} />
          </div>
          {degraded ? <p className="stale-recommendation">Live model, trajectory and queue ETA are unavailable. This retained recommendation is context only; use the clinician category, fixed wait bound and local escalation protocol.</p> : null}
          <div className="deadline-pair">
            <div><span>{degraded ? "Fixed bound" : "Recommended within"}</span><strong>{formatActionWindow(rec.action_window.maximum_minutes)}</strong></div>
            <div><span>Predicted action</span><strong>{degraded ? "Unavailable" : formatEta(rec.predicted_time_to_action_minutes)}</strong></div>
          </div>
          {!degraded ? <SlackLine
            deadline={rec.action_window.maximum_minutes}
            eta={rec.predicted_time_to_action_minutes}
            slack={rec.clinical_slack_minutes}
            conflict={rec.capacity_conflict}
          /> : null}
          <p className="basis-line">Bounded by {rec.action_window.basis.map((item) => item.replaceAll("_", " ")).join(" + ")}</p>
        </section>

        <section className="inspector-section" aria-labelledby="trajectory-heading">
          <div className="section-heading-row">
            <div><h3 id="trajectory-heading">Trajectory</h3><p>Calibrated critical-risk horizons</p></div>
            {!degraded ? <RiskSparkline values={patient.trajectory} conflict={rec.capacity_conflict} /> : <span className="stale-value">Last verified</span>}
          </div>
          <div className="risk-horizons">
            {["5", "15", "30", "60"].map((horizon) => (
              <div key={horizon}><span>{horizon}m</span><strong>{Math.round(rec.risk_by_horizon[horizon] * 100)}%</strong></div>
            ))}
          </div>
          <div className="vitals-grid">
            <Vital label="HR" value={current.heart_rate_bpm} suffix=" bpm" prior={prior.heart_rate_bpm} />
            <Vital label="SpO₂" value={current.spo2_percent} suffix="%" prior={prior.spo2_percent} />
            <Vital label="RR" value={current.respiratory_rate_per_min} suffix="/m" prior={prior.respiratory_rate_per_min} />
            <Vital label="BP" value={current.systolic_bp_mmhg} suffix={`/${current.diastolic_bp_mmhg ?? "—"}`} prior={prior.systolic_bp_mmhg} />
          </div>
        </section>

        <section className="inspector-section" aria-labelledby="explanation-heading">
          <div className="section-heading-row">
            <div><h3 id="explanation-heading">Why this action</h3><p>Current recommendation, not a diagnosis</p></div>
            <span className="reliability"><Database size={13} aria-hidden="true" /> {Math.round(rec.uncertainty.data_quality_score * 100)}% data quality</span>
          </div>
          <div className="explanation-group">
            <strong>What changed</strong>
            <ul>{rec.explanation.what_changed.map((item) => <li key={item}>{item.replaceAll("_", " ")}</li>)}</ul>
          </div>
          <div className="explanation-group">
            <strong>Factors used</strong>
            <ul>{rec.explanation.top_factors.slice(0, 3).map((item) => <li key={item}>{item.replaceAll("_", " ")}</li>)}</ul>
          </div>
          {rec.safety.rule_hits.length ? (
            <div className="rule-band"><ShieldAlert size={15} aria-hidden="true" /><span><strong>Safety rules determine this action</strong>{rec.safety.rule_hits.join(", ").replaceAll("_", " ")} · model output cannot relax the rule outcome</span></div>
          ) : null}
        </section>

        {rec.next_best_observation ? (
          <section className="next-observation" aria-labelledby="nbo-heading">
            <Stethoscope size={19} aria-hidden="true" />
            <div>
              <span id="nbo-heading">Next Best Observation</span>
              <strong>{rec.next_best_observation.label}</strong>
              <p>Within {formatActionWindow(rec.next_best_observation.recommended_within_minutes)} · low burden · highest expected decision value among available observations ({Math.round(rec.next_best_observation.expected_decision_value * 100)}%). First step only: if unavailable or uncertainty persists, complete the full reassessment or escalate.</p>
            </div>
          </section>
        ) : null}

        {rec.safety.safe_mode ? (
          <section className="safe-mode-block">
            <Activity size={18} aria-hidden="true" />
            <div><strong>Safe Mode is active</strong><p>{rec.safety.safe_mode_reasons.join(" ") || "Uncertainty requires clinician review."} Priority is preserved or increased.</p></div>
          </section>
        ) : null}

        <DecisionPanel patient={patient} />
      </div>
      <footer className="inspector-foot">Model {rec.component_versions.model} · Rules {rec.component_versions.rules} · Recommendation {rec.recommendation_id}</footer>
    </aside>
  );
}
