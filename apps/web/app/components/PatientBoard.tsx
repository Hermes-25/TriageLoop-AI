"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, ChevronRight, Play, RefreshCw, Search } from "lucide-react";
import { formatAction, formatActionWindow, formatEta, formatMinutes, RiskSparkline, StatusMark } from "@/app/components/ClinicalVisuals";
import { PatientInspector } from "@/app/components/PatientInspector";
import { useProduct } from "@/app/components/ProductProvider";
import { TriageLoader } from "@/app/components/TriageLoader";

type Filter = "all" | "attention" | "conflict" | "safe_mode";

export function PatientBoard() {
  const { state, selectedPatient, selectedId, loading, pending, degraded, error, selectPatient, refresh, setScenario, runDeterioration } = useProduct();
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [inspectorOpen, setInspectorOpen] = useState(false);

  useEffect(() => {
    const requestedPatient = new URLSearchParams(window.location.search).get("patient");
    if (requestedPatient && /^P-\d{4}$/.test(requestedPatient)) {
      selectPatient(requestedPatient);
      setInspectorOpen(true);
    }
  }, []);

  function openPatient(patientId: string) {
    selectPatient(patientId);
    setInspectorOpen(true);
  }

  async function applyDeterioration() {
    await runDeterioration();
    setInspectorOpen(true);
  }

  const patients = useMemo(() => {
    if (!state) return [];
    const normalized = query.trim().toLowerCase();
    return state.patients.filter((patient) => {
      const rec = patient.recommendation;
      const filterMatch = filter === "all"
        || (filter === "attention" && ["immediate_review", "reassess", "safe_mode_review"].includes(rec.recommended_action))
        || (filter === "conflict" && rec.capacity_conflict)
        || (filter === "safe_mode" && rec.safety.safe_mode);
      const queryMatch = !normalized || `${patient.patient_id} ${patient.chief_complaint} ${patient.age_band}`.toLowerCase().includes(normalized);
      return filterMatch && queryMatch;
    });
  }, [state, filter, query]);

  if (loading) {
    return <TriageLoader />;
  }

  if (error && !state) {
    return (
      <main className="page-centered">
        <div className="error-state"><AlertTriangle size={26} aria-hidden="true" /><h1>Decision service unavailable</h1><p>{error}</p><button className="button primary" type="button" onClick={() => void refresh()}>Retry connection</button></div>
      </main>
    );
  }

  if (!state || !selectedPatient) return null;

  return (
    <main className="board-page">
      <section className={`capacity-banner ${degraded ? "degraded" : state.capacity.state}`} aria-label="Current decision-service and capacity state">
        <div className="capacity-state"><span className="capacity-symbol" aria-hidden="true">{degraded ? "!" : state.capacity.state === "constrained" ? "!" : "✓"}</span><div><strong>{degraded ? "Degraded mode — live estimates paused" : state.capacity.state === "constrained" ? "Capacity constrained" : "Capacity available"}</strong><p>{degraded ? "Last verified board retained. Follow clinician category, fixed wait bounds and local escalation protocol; no automated downgrade." : state.capacity.message}</p></div></div>
        <div className="scenario-control" aria-label="Queue scenario">
          <button type="button" aria-pressed={state.scenario === "baseline"} onClick={() => setScenario("baseline")} disabled={pending || degraded}>Baseline</button>
          <button type="button" aria-pressed={state.scenario === "surge_3x"} onClick={() => setScenario("surge_3x")} disabled={pending || degraded}>3× surge</button>
        </div>
      </section>

      {error ? <div className="inline-error" role="alert">{error}<button type="button" onClick={() => void refresh()}>Retry</button></div> : null}

      <div className={`board-workspace ${inspectorOpen ? "inspector-open" : ""}`}>
        <section className="queue-panel" aria-labelledby="queue-heading" aria-busy={pending}>
          <header className="queue-header">
            <div>
              <h1 id="queue-heading">Live action queue</h1>
              <p><strong>{state.summary.waiting} simulated patients</strong> shown from a 28-case test library · ranked by clinical level, Action Window and Clinical Slack</p>
            </div>
            <div className="queue-summary" aria-label="Queue summary">
              <span><strong>{state.summary.waiting}</strong> waiting</span>
              <span><strong>{state.summary.reassessment_due}</strong> action due</span>
              <span className={state.summary.capacity_conflicts ? "has-conflict" : ""}><strong>{state.summary.capacity_conflicts}</strong> conflicts</span>
            </div>
          </header>

          <div className="queue-tools">
            <div className="filter-tabs" role="group" aria-label="Filter patients">
              {(["all", "attention", "conflict", "safe_mode"] as Filter[]).map((item) => (
                <button key={item} type="button" aria-pressed={filter === item} onClick={() => setFilter(item)}>{item === "safe_mode" ? "Safe Mode" : item[0].toUpperCase() + item.slice(1)}</button>
              ))}
            </div>
            <label className="search-control">
              <Search size={15} aria-hidden="true" />
              <span className="sr-only">Search patient queue</span>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find patient" />
            </label>
            <button className="demo-action" type="button" onClick={() => void applyDeterioration()} disabled={pending || degraded || state.deterioration_applied}>
              {pending ? <RefreshCw className="spin" size={15} aria-hidden="true" /> : <Play size={15} fill="currentColor" aria-hidden="true" />}
              {state.deterioration_applied ? "Deterioration applied" : "Run deterioration event"}
            </button>
          </div>

          <div className="table-scroll">
            <table className="patient-table">
              <caption className="sr-only">Waiting patients ordered by TriageLoop queue priority</caption>
              <thead><tr><th scope="col">#</th><th scope="col">Patient</th><th scope="col">Action now</th><th scope="col">Trajectory</th><th scope="col">By</th><th scope="col">ETA</th><th scope="col">Slack</th><th scope="col"><span className="sr-only">Open</span></th></tr></thead>
              <tbody>
                {patients.map((patient) => {
                  const rec = patient.recommendation;
                  const selected = patient.patient_id === selectedId;
                  const currentConflict = !degraded && rec.capacity_conflict;
                  return (
                    <tr key={patient.patient_id} className={selected ? "selected" : ""}>
                      <td className="rank-cell"><button type="button" onClick={() => openPatient(patient.patient_id)} aria-label={`Open ${patient.patient_id}, queue position ${patient.queue_position}`}>{patient.queue_position}</button></td>
                      <td>
                        <button className="patient-cell" type="button" onClick={() => openPatient(patient.patient_id)}>
                          <span className={`level-disc level-${patient.clinician_level}`}>{patient.clinician_level}</span>
                          <span><strong>{patient.patient_id}</strong><small>{patient.age_band} · {patient.age_years}y · {patient.wait_minutes}m</small><em>{patient.chief_complaint}</em></span>
                        </button>
                      </td>
                      <td>
                          <span className="action-cell"><strong>{formatAction(rec.recommended_action)}</strong>{degraded ? <StatusMark kind="warning" label="Rules fallback" /> : rec.safety.safe_mode ? <StatusMark kind="warning" label="Safe Mode" /> : currentConflict ? <StatusMark kind="critical" label="Conflict" /> : <span>{rec.uncertainty.state} uncertainty</span>}</span>
                        </td>
                      <td>{degraded ? <span className="stale-value">Last verified</span> : <RiskSparkline values={patient.trajectory} conflict={currentConflict} />}</td>
                      <td className="time-cell"><strong>{formatActionWindow(rec.action_window.maximum_minutes)}</strong></td>
                      <td className="time-cell"><span>{degraded ? "Stale" : formatEta(rec.predicted_time_to_action_minutes)}</span></td>
                      <td className={currentConflict ? "slack-cell conflict" : "slack-cell"}><strong>{degraded ? "—" : formatMinutes(rec.clinical_slack_minutes, true)}</strong><small>{degraded ? "unavailable" : currentConflict ? "infeasible" : "remaining"}</small></td>
                      <td><button className="open-row" type="button" onClick={() => openPatient(patient.patient_id)} aria-label={`View details for ${patient.patient_id}`}><ChevronRight size={16} aria-hidden="true" /></button></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {patients.length === 0 ? <div className="empty-table"><strong>No patients match this view</strong><p>Clear the filter or search to return to the active queue.</p></div> : null}
          </div>
          <footer className="queue-foot"><span>{degraded ? "Last verified" : "Model state as of"} {new Date(state.generated_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false })}</span><span>Live via SSE · polling fallback available</span><span>{state.prototype_notice}</span></footer>
        </section>
        <PatientInspector patient={selectedPatient} degraded={degraded} onClose={() => setInspectorOpen(false)} />
      </div>
    </main>
  );
}
