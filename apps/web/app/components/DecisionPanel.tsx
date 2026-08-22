"use client";

import { useState } from "react";
import { Check, PencilLine, ShieldCheck } from "lucide-react";
import { useProduct } from "@/app/components/ProductProvider";
import type { Patient } from "@/app/lib/types";

const ACTION_OPTIONS = [
  ["reassess now", "Reassess now"],
  ["increase priority", "Increase priority"],
  ["move to monitored space", "Move to monitored space"],
  ["continue monitored wait", "Continue monitored wait"],
];

export function DecisionPanel({ patient }: { patient: Patient }) {
  const { recordDecision, pending, degraded } = useProduct();
  const [mode, setMode] = useState<"modify" | "override" | null>(null);
  const [reason, setReason] = useState("");
  const [modifiedAction, setModifiedAction] = useState(ACTION_OPTIONS[0][0]);
  const [localError, setLocalError] = useState("");

  async function submitDetailed() {
    if (!mode) return;
    if (!reason.trim()) {
      setLocalError("Add the clinical reason before recording this decision.");
      return;
    }
    setLocalError("");
    await recordDecision(patient.patient_id, { action: mode, reason: reason.trim(), modified_action: modifiedAction });
    setMode(null);
    setReason("");
  }

  return (
    <section className="decision-section" aria-labelledby="decision-heading">
      <div className="section-heading-row">
        <div>
          <h3 id="decision-heading">Clinician decision</h3>
          <p>Human action is recorded against this exact recommendation.</p>
        </div>
        {patient.decision_state ? <span className="recorded-state"><Check size={13} aria-hidden="true" /> Recorded</span> : null}
      </div>

      {patient.decision_state ? (
        <div className="decision-receipt">
          <ShieldCheck size={18} aria-hidden="true" />
          <div><strong>{patient.decision_state.replace(":", " · ")}</strong><span>Audit chain updated · no autonomous downgrade</span></div>
        </div>
      ) : (
        <>
          {degraded ? <div className="downtime-note"><strong>Digital recording paused</strong><span>Use the local downtime record; reconcile it to this patient after service restoration.</span></div> : null}
          <div className="decision-actions">
            <button className="button primary" type="button" disabled={pending || degraded} onClick={() => void recordDecision(patient.patient_id, { action: "accept" })}>
              <Check size={16} aria-hidden="true" /> Accept action
            </button>
            <button className="button secondary" type="button" disabled={pending || degraded} onClick={() => setMode("modify")}>
              <PencilLine size={15} aria-hidden="true" /> Modify
            </button>
            <button className="button quiet-danger" type="button" disabled={pending || degraded} onClick={() => setMode("override")}>
              Override
            </button>
          </div>
          {mode ? (
            <div className="inline-decision-form">
              <div className="inline-form-head">
                <strong>{mode === "override" ? "Override recommendation" : "Modify recommended action"}</strong>
                <button className="text-button" type="button" onClick={() => setMode(null)}>Cancel</button>
              </div>
              <label>
                Clinician action
                <select value={modifiedAction} onChange={(event) => setModifiedAction(event.target.value)}>
                  {ACTION_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </label>
              <label>
                Clinical reason
                <textarea value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Document what you observed or judged differently" rows={3} />
              </label>
              {localError ? <p className="field-error" role="alert">{localError}</p> : null}
              <button className="button primary" type="button" disabled={pending} onClick={() => void submitDetailed()}>
                Record {mode}
              </button>
            </div>
          ) : null}
        </>
      )}
    </section>
  );
}
