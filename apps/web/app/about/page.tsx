import type { Metadata } from "next";
import { ArrowRight, BookOpenCheck, Database, ShieldCheck, UserCheck } from "lucide-react";
import { ResilienceDemo } from "@/app/components/ResilienceDemo";

export const metadata: Metadata = { title: "About" };

const FLOW = [
  ["Patient trajectory", "Vitals, symptoms, history and freshness", Database],
  ["Safety + uncertainty", "Age-aware rules, conformal sets and Safe Mode", ShieldCheck],
  ["Action Window", "Conservative recommended-within interval", BookOpenCheck],
  ["Clinical Slack", "Action Window minus predicted queue time", ArrowRight],
  ["Clinician decision", "Accept, modify or override with audit", UserCheck],
] as const;

export default function AboutPage() {
  return (
    <main className="content-page about-page">
      <header className="page-header"><h1>From a score to a deadline-aware care loop</h1><p>TriageLoop is a research prototype for continuously managing patients who are already waiting—not an autonomous triage device.</p></header>
      <section className="system-flow" aria-label="TriageLoop system flow">
        {FLOW.map(([title, detail, Icon], index) => (
          <div className="flow-step" key={title}><Icon size={21} aria-hidden="true" /><span><strong>{title}</strong><small>{detail}</small></span>{index < FLOW.length - 1 ? <ArrowRight className="flow-arrow" size={17} aria-hidden="true" /> : null}</div>
        ))}
      </section>
      <div className="about-columns">
        <section className="plain-section"><h2>What is genuinely different</h2><ul className="feature-list"><li><strong>Action Window</strong><span>The product answers “by when should we act?” instead of stopping at a risk score.</span></li><li><strong>Clinical Slack</strong><span>Clinical need is compared with operational feasibility, exposing—not hiding—capacity conflict.</span></li><li><strong>Next Best Observation</strong><span>Uncertainty becomes a low-burden information-gathering action.</span></li><li><strong>Closed loop</strong><span>Deterioration updates the deadline, queue position, explanation and audit trail.</span></li></ul></section>
        <section className="plain-section"><h2>Safety boundaries</h2><ul className="boundary-list"><li>Rules are evaluated before the model.</li><li>No autonomous downgrade is permitted.</li><li>Uncertainty escalates attention or activates Safe Mode.</li><li>Queue pressure never relaxes clinical need.</li><li>An LLM is not used in any quantitative clinical path.</li><li>Every clinical surface is explicitly labeled as synthetic.</li></ul></section>
      </div>
      <ResilienceDemo />
      <section className="governance-band"><div><span>Prototype jurisdiction</span><strong>India</strong></div><p>Designed to the DPDP Act and 2025 Rules baseline. Rules 3, 5–16, 22 and 23 commence 18 months after the 13 November 2025 Gazette publication—13 May 2027. ABDM policy and Indian EHR standards guide the prototype regardless of that phase-in. Synthetic data only; no compliance or certification claim.</p></section>
      <p className="page-notice">Synthetic decision-support prototype — not validated for clinical use.</p>
    </main>
  );
}
