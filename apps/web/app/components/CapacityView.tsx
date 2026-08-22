"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, ArrowDownRight, CheckCircle2, ServerCog } from "lucide-react";
import { useProduct } from "@/app/components/ProductProvider";
import { productApi } from "@/app/lib/api";
import { formatActionWindow, formatEta, formatMinutes } from "@/app/components/ClinicalVisuals";
import type { Evaluation } from "@/app/lib/types";

function UtilizationBar({ label, value }: { label: string; value: number }) {
  const constrained = value >= 0.8;
  return (
    <div className="utilization-row">
      <div><span>{label}</span><strong>{Math.round(value * 100)}%</strong></div>
      <div className="utilization-track" aria-label={`${label} utilization ${Math.round(value * 100)} percent`}><span className={constrained ? "constrained" : ""} style={{ width: `${Math.min(100, value * 100)}%` }} /></div>
    </div>
  );
}

export function CapacityView() {
  const { state, pending, degraded, setScenario } = useProduct();
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);

  useEffect(() => { void productApi.evaluation().then(setEvaluation); }, []);

  if (!state) return <main className="content-page"><div className="content-skeleton" /></main>;

  const conflictPatients = state.patients.filter((patient) => patient.recommendation.capacity_conflict);
  return (
    <main className="content-page">
      <header className="page-header split-heading">
        <div><h1>Capacity truth</h1><p>Clinical need remains fixed. This view shows whether the queue can deliver it.</p></div>
        <div className="scenario-control large" aria-label="Capacity scenario">
          <button type="button" aria-pressed={state.scenario === "baseline"} onClick={() => setScenario("baseline")} disabled={pending || degraded}>Baseline</button>
          <button type="button" aria-pressed={state.scenario === "surge_3x"} onClick={() => setScenario("surge_3x")} disabled={pending || degraded}>3× surge</button>
        </div>
      </header>

      <section className={`capacity-hero ${degraded ? "degraded" : state.capacity.state}`}>
        <div className="capacity-hero-copy">
          <span className="capacity-symbol" aria-hidden="true">{degraded || state.capacity.state === "constrained" ? "!" : "✓"}</span>
          <div><span>Regional ED · {state.scenario_label}</span><h2>{degraded ? "Live capacity estimate unavailable" : state.capacity.state === "constrained" ? "Some clinical deadlines are not feasible" : "The current queue is feasible"}</h2><p>{degraded ? "Last verified resource state retained. Follow fixed category deadlines and local escalation protocol until the service is restored." : state.capacity.message}</p></div>
        </div>
        <div className="capacity-count"><strong>{state.summary.capacity_conflicts}</strong><span>negative-Slack patients</span></div>
      </section>

      <div className="capacity-layout">
        <section className="plain-section" aria-labelledby="resource-heading">
          <div className="section-title"><div><h2 id="resource-heading">Resource pressure</h2><p>Queue Twin estimate at 10:42 IST</p></div><ServerCog size={20} aria-hidden="true" /></div>
          <div className="utilization-list">
            <UtilizationBar label="Clinician" value={state.capacity.clinician_utilization} />
            <UtilizationBar label="Reassessment nurse" value={state.capacity.reassessment_utilization} />
            <UtilizationBar label="Monitored space" value={state.scenario === "surge_3x" ? 0.79 : 0.48} />
            <UtilizationBar label="Treatment space" value={state.scenario === "surge_3x" ? 0.4 : 0.29} />
          </div>
          <div className="capacity-note"><AlertTriangle size={16} aria-hidden="true" /><p>Priority reallocation improves who is seen first; it does not create staff or space. Escalation remains an operational decision.</p></div>
        </section>

        <section className="plain-section" aria-labelledby="conflict-heading">
          <div className="section-title"><div><h2 id="conflict-heading">Deadline conflicts</h2><p>Patients whose predicted action exceeds their Action Window</p></div></div>
          {conflictPatients.length ? (
            <div className="conflict-list">
              {conflictPatients.slice(0, 6).map((patient) => (
                <div className="conflict-row" key={patient.patient_id}>
                  <span className={`level-disc level-${patient.clinician_level}`}>{patient.clinician_level}</span>
                  <div><strong>{patient.patient_id} · {patient.chief_complaint}</strong><span>By {formatActionWindow(patient.recommendation.action_window.maximum_minutes)} · ETA {degraded ? "stale" : formatEta(patient.recommendation.predicted_time_to_action_minutes)}</span></div>
                  <strong>{degraded ? "—" : formatMinutes(patient.recommendation.clinical_slack_minutes)}</strong>
                </div>
              ))}
            </div>
          ) : <div className="positive-empty"><CheckCircle2 size={21} aria-hidden="true" /><div><strong>No visible conflicts</strong><p>All current Action Windows are predicted to be met.</p></div></div>}
        </section>
      </div>

      <section className="evidence-strip" aria-labelledby="simulation-heading">
        <div className="evidence-strip-title"><span>Queue Twin evidence</span><h2 id="simulation-heading">What changes under 3× demand</h2><p>Paired synthetic shifts · static five-level triage versus TriageLoop</p></div>
        {evaluation ? (
          <div className="evidence-results">
            <div><ArrowDownRight size={19} aria-hidden="true" /><strong>{Math.round(evaluation.overall_surge.action_window_miss_rate.relative_improvement * 100)}%</strong><span>fewer misses in the registered synthetic 30-minute-response experiment*</span></div>
            <div><ArrowDownRight size={19} aria-hidden="true" /><strong>{Math.round(evaluation.overall_surge.negative_slack_minutes.relative_improvement * 100)}%</strong><span>less negative-Slack time</span></div>
            <div><ArrowDownRight size={19} aria-hidden="true" /><strong>{Math.round(evaluation.overall_surge.mean_signal_to_action_minutes.relative_improvement * 100)}%</strong><span>shorter signal-to-action</span></div>
          </div>
        ) : <div className="inline-loader">Loading paired-shift evidence…</div>}
      </section>
      <p className="page-notice">* Self-authored synthetic generator and simulator; the reduction does not hold at the strictest 10-minute response definition. Not clinical or staffing evidence.</p>
    </main>
  );
}
