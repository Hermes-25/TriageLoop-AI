"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Link2, Search } from "lucide-react";
import { productApi } from "@/app/lib/api";
import type { AuditEvent, AuditIntegrity } from "@/app/lib/types";

function auditDetail(event: AuditEvent) {
  const action = typeof event.payload.clinician_action === "string" ? event.payload.clinician_action : null;
  const reason = typeof event.payload.reason === "string" ? event.payload.reason : null;
  const changes = Array.isArray(event.payload.what_changed) ? event.payload.what_changed.join(" · ") : null;
  if (action && reason) return `${action.replaceAll("_", " ")} — ${reason}`;
  if (changes) return changes;
  if (typeof event.payload.clinical_slack_minutes === "number") return `${event.payload.clinical_slack_minutes}m Clinical Slack`;
  return null;
}

export function AuditView() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [query, setQuery] = useState("");
  const [integrity, setIntegrity] = useState<AuditIntegrity | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    void Promise.all([productApi.audit(), productApi.auditIntegrity()])
      .then(([nextEvents, nextIntegrity]) => { setEvents(nextEvents); setIntegrity(nextIntegrity); })
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false));
  }, []);
  const filtered = useMemo(() => {
    const value = query.trim().toLowerCase();
    return events.filter((event) => !value || `${event.patient_id} ${event.event_type} ${event.actor}`.toLowerCase().includes(value));
  }, [events, query]);
  return (
    <main className="content-page">
      <header className="page-header split-heading">
        <div><h1>Decision audit</h1><p>Every material observation, recommendation and clinician response is appended—not overwritten.</p></div>
        <div className={`chain-status ${integrity && !integrity.intact ? "broken" : ""}`}><CheckCircle2 size={18} aria-hidden="true" /><span><strong>{integrity ? integrity.intact ? "Chain verified" : "Integrity failure" : "Checking chain"}</strong>{integrity?.events_checked ?? events.length} events checked</span></div>
      </header>
      {error ? <div className="inline-error" role="alert">Audit verification unavailable: {error}</div> : null}
      <section className="plain-section audit-section">
        <div className="audit-tools"><label className="search-control wide"><Search size={15} aria-hidden="true" /><span className="sr-only">Filter audit events</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filter patient, event or actor" /></label><span>Newest first · prototype SHA-256 integrity chain</span></div>
        {loading ? <div className="content-skeleton compact" /> : (
          <div className="audit-table-wrap">
            <table className="audit-table">
              <thead><tr><th scope="col">Seq.</th><th scope="col">Patient</th><th scope="col">Event</th><th scope="col">Actor</th><th scope="col">Timestamp</th><th scope="col">Integrity</th></tr></thead>
              <tbody>{filtered.map((event) => {
                const detail = auditDetail(event);
                return (
                <tr key={event.event_id}>
                  <td className="mono">{event.sequence.toString().padStart(3, "0")}</td>
                  <td className="mono">{event.patient_id ?? "SYSTEM"}</td>
                  <td><strong>{event.event_type.replaceAll("_", " ")}</strong>{detail ? <span className="audit-detail">{detail}</span> : null}<small>{event.event_id}</small></td>
                  <td>{event.actor.replaceAll("_", " ")}</td>
                  <td>22 Aug · 10:42:00</td>
                  <td><span className="hash-chip"><Link2 size={12} aria-hidden="true" />{event.event_hash.slice(0, 9)}</span></td>
                </tr>
              )})}</tbody>
            </table>
            {!filtered.length ? <div className="empty-table"><strong>No audit events match</strong><p>Try a patient ID such as P-0009 or an event such as override.</p></div> : null}
          </div>
        )}
      </section>
      <p className="page-notice">The hash chain demonstrates tamper-evident linkage for the prototype; it is not a claim of production immutability.</p>
    </main>
  );
}
