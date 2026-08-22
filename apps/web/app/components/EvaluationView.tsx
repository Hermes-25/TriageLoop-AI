"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Check, FlaskConical, Info } from "lucide-react";
import { productApi } from "@/app/lib/api";
import type { Evaluation } from "@/app/lib/types";

const METRIC_LABELS: Record<string, string> = {
  action_window_miss_rate: "Action Window miss rate",
  negative_slack_minutes: "Negative-Slack minutes",
  mean_signal_to_action_minutes: "Signal-to-action time",
  low_acuity_p90_wait_minutes: "Low-acuity P90 wait",
};

function pct(value: number) { return `${(value * 100).toFixed(1)}%`; }

function gateCopy(key: string) {
  if (key === "low_acuity_p90_no_more_than_20pct_worse") return "Low-acuity guardrail: tail wait must not be more than 20% worse";
  if (key === "surge_action_window_relative_reduction_at_least_20pct") return "Registered 30-minute-response gate: at least 20% fewer misses";
  if (key === "all_cells_have_100_replications") return "100 paired replications completed in every registered cell";
  return key.replaceAll("_", " ");
}

export function EvaluationView() {
  const [data, setData] = useState<Evaluation | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { void productApi.evaluation().then(setData).catch((reason: Error) => setError(reason.message)); }, []);

  return (
    <main className="content-page evidence-page">
      <header className="page-header split-heading">
        <div><h1>Evaluation evidence</h1><p>Predeclared operational gates, full paired comparisons and honest residual risk.</p></div>
        <div className="evidence-stamp"><FlaskConical size={18} aria-hidden="true" /><span><strong>Registered + verification runs</strong>Seed {data?.base_seed ?? 20260822} · 1,800 three-policy + {(data?.verification_policy_shifts ?? 1200).toLocaleString("en-IN")} two-policy shifts</span></div>
      </header>
      {error ? <div className="inline-error" role="alert">{error}</div> : null}
      {!data ? <div className="content-skeleton" /> : (
        <>
          <section className="evidence-boundary" aria-label="Evidence boundary">
            <AlertTriangle size={18} aria-hidden="true" />
            <div><strong>Synthetic-system evidence—not external clinical validation</strong><p>The generator, model and Queue Twin were authored within this project. Results establish internal behavior under declared assumptions; they do not show transfer to a real emergency department.</p></div>
          </section>
          <section className="gate-band" aria-label="Evaluation gates">
            {Object.entries(data.gates).map(([key, passed]) => (
              <div key={key}><span className={passed ? "gate-pass" : "gate-fail"}>{passed ? <Check size={14} aria-hidden="true" /> : "!"}</span><span><strong>{passed ? "Passed" : "Failed"}</strong>{gateCopy(key)}</span></div>
            ))}
          </section>

          <section className="verification-insights" aria-label="TL-05 verification findings">
            <article className="verification-card passed">
              <span>Stronger comparator</span>
              <strong>↓ {pct(data.periodic_retriage.overall_surge.action_window_miss_rate.relative_improvement)}</strong>
              <p>Fewer surge misses than fixed {data.periodic_retriage.minutes}-minute periodic re-triage (95% CI {pct(data.periodic_retriage.overall_surge.action_window_miss_rate.ci95_low)}–{pct(data.periodic_retriage.overall_surge.action_window_miss_rate.ci95_high)}). Synthetic simulation only.</p>
            </article>
            <article className="verification-card failed">
              <span>Single-observation NBO gate</span>
              <strong>Failed</strong>
              <p>{pct(data.nbo_verification.comparison.observation_count_reduction)} fewer observations, but {(Math.abs(data.nbo_verification.comparison.operational_recall_difference_nbo_minus_fixed) * 100).toFixed(1)} percentage points lower operational critical recall. It remains a first step, not a replacement for full reassessment.</p>
            </article>
            <article className="verification-card external">
              <span>External input check</span>
              <strong>{data.external_plausibility.coverage.external_measurements.toLocaleString("en-IN")}</strong>
              <p>Open MIMIC-IV demo measurements mapped across {data.external_plausibility.coverage.mapped_core_fields} core vital fields. Input-scale plausibility only—not ED or clinical validation.</p>
            </article>
          </section>

          <section className="evidence-boundary" aria-label="Periodic comparator response-definition sensitivity">
            <Info size={18} aria-hidden="true" />
            <div><strong>Stronger-comparator sensitivity is positive—but not universally 20%+</strong><p>Versus fixed 15-minute periodic re-triage, miss-rate reductions at 10/20/30-minute response definitions are {pct(data.periodic_retriage.response_sensitivity["10"].relative_improvement)} / {pct(data.periodic_retriage.response_sensitivity["20"].relative_improvement)} / {pct(data.periodic_retriage.response_sensitivity["30"].relative_improvement)}. Only 30 minutes exceeds 20%; this post-verification analysis is not a retroactively registered gate.</p></div>
          </section>

          <div className="evaluation-layout">
            <section className="plain-section evidence-table-section">
              <div className="section-title"><div><h2>Overall 3× surge</h2><p>Mean across community, regional and urban-trauma profiles</p></div></div>
              <div className="evaluation-table-wrap">
                <table className="evaluation-table">
                  <thead><tr><th scope="col">Registered outcome</th><th scope="col">Static triage</th><th scope="col">TriageLoop</th><th scope="col">Relative change</th><th scope="col">95% CI</th></tr></thead>
                  <tbody>
                    {Object.entries(data.overall_surge).map(([key, metric]) => (
                      <tr key={key}>
                        <th scope="row">{METRIC_LABELS[key] ?? key}</th>
                        <td>{key.includes("rate") ? pct(metric.static_mean) : `${metric.static_mean.toFixed(1)}m`}</td>
                        <td><strong>{key.includes("rate") ? pct(metric.triageloop_mean) : `${metric.triageloop_mean.toFixed(1)}m`}</strong></td>
                        <td className="improvement">↓ {pct(metric.relative_improvement)}{key === "action_window_miss_rate" ? <sup>*</sup> : null}</td>
                        <td>{pct(metric.ci95_low)}–{pct(metric.ci95_high)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <aside className="method-rail">
              <h2>Experiment contract</h2>
              <dl>
                <div><dt>Policies</dt><dd>FIFO · initial static · 15-minute periodic re-triage · TriageLoop</dd></div>
                <div><dt>Static comparator</dt><dd>Initial category, then arrival order within category; later observations are not processed.</dd></div>
                <div><dt>Sites</dt><dd>100 · 300 · 550 visits/day</dd></div>
                <div><dt>Demand</dt><dd>Baseline · 3× surge</dd></div>
                <div><dt>Replications</dt><dd>100 paired shifts per cell</dd></div>
                <div><dt>Primary quantity</dt><dd>Clinical Slack</dd></div>
              </dl>
              <div className="method-note"><Info size={16} aria-hidden="true" /><p>Results establish simulated prioritisation performance, not clinical benefit, staffing adequacy or production readiness.</p></div>
            </aside>
          </div>

          <section className="site-comparison" aria-labelledby="site-heading">
            <div className="section-title"><div><h2 id="site-heading">Residual risk by site</h2><p>TriageLoop surfaces capacity failure even where it improves prioritisation.</p></div></div>
            <div className="site-rows">
              {Object.entries(data.site_results).map(([site, result]) => {
                const staticMiss = result.static.action_window_miss_rate;
                const tlMiss = result.triageloop.action_window_miss_rate;
                return (
                  <div className="site-row" key={site}>
                    <div><strong>{site.replace("_", " ")}</strong><span>{Math.round(result.triageloop.critical_recall * 100)}% critical recall</span></div>
                    <div className="comparison-bars" aria-label={`${site}: static miss ${pct(staticMiss)}, TriageLoop miss ${pct(tlMiss)}`}>
                      <span className="static-bar" style={{ width: `${Math.max(2, staticMiss * 200)}%` }}><i /></span>
                      <span className="tl-bar" style={{ width: `${Math.max(2, tlMiss * 200)}%` }}><i /></span>
                    </div>
                    <div><span>Static {pct(staticMiss)}</span><strong>TriageLoop {pct(tlMiss)}</strong></div>
                  </div>
                );
              })}
            </div>
            <div className="chart-legend"><span><i className="legend-static" /> Static five-level</span><span><i className="legend-tl" /> TriageLoop</span></div>
            {data.site_comparisons.community ? <div className="community-caveat"><AlertTriangle size={16} aria-hidden="true" /><p><strong>Small-site residual risk:</strong> Community simulation improves by {pct(data.site_comparisons.community.relative_improvement)} (95% CI {pct(data.site_comparisons.community.ci95_low)}–{pct(data.site_comparisons.community.ci95_high)}), but its TriageLoop miss rate remains {pct(data.site_comparisons.community.triageloop_mean)}. Software does not substitute for capacity.</p></div> : null}
          </section>

          <section className="plain-section alert-workload" aria-labelledby="alert-workload-heading">
            <div className="section-title"><div><h2 id="alert-workload-heading">Consolidated review workload</h2><p>Model/rule changes collapsed to one patient-level alert · descriptive simulation output, not a safe staffing threshold</p></div></div>
            <div className="evaluation-table-wrap">
              <table className="evaluation-table">
                <thead><tr><th scope="col">Site</th><th scope="col">Load</th><th scope="col">Reassessment nurses</th><th scope="col">Alerts / 8h shift</th><th scope="col">Alerts / waiting-patient-hour</th><th scope="col">Alerts / nurse-hour</th></tr></thead>
                <tbody>{Object.entries(data.alert_workload).flatMap(([site, loads]) => Object.entries(loads).map(([load, workload]) => (
                  <tr key={`${site}-${load}`}><th scope="row">{site.replace("_", " ")}</th><td>{load === "surge_3x" ? "3× surge" : "Baseline"}</td><td>{workload.reassessment_nurses}</td><td>{workload.mean_consolidated_alerts_per_8h_shift.toFixed(1)}</td><td>{workload.mean_alerts_per_waiting_patient_hour.toFixed(2)}</td><td><strong>{workload.mean_alerts_per_reassessment_nurse_hour.toFixed(2)}</strong></td></tr>
                )))}</tbody>
              </table>
            </div>
          </section>
        </>
      )}
      <p className="page-notice">* The 36.0% registered result uses the weaker initial-category static comparator and a 30-minute composite response allowance. Its 10-minute sensitivity was {data ? pct(data.deterioration_response_sensitivity["10"].relative_improvement) : "11.1%"}. Stronger periodic-comparator sensitivity is reported separately above. Synthetic data only; not validated for clinical use.</p>
    </main>
  );
}
