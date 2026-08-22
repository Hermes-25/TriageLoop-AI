# Risk Register

Scale: likelihood and impact are Low / Medium / High. Owner is the TriageLoop project team unless an external action requires explicit team approval.

| ID | Risk | Likelihood | Impact | Prevention/mitigation | Trigger and fallback |
|---|---|---:|---:|---|---|
| R-01 | Synthetic data appears clinically arbitrary | Medium | High | Publish generator assumptions; use coherent trajectories, curated edge cases and rule-based plausibility checks | Clinical contradictions in review -> simplify generator and disclose limits; do not tune presentation around implausible cases |
| R-02 | Model complexity adds no credible value | Low | Medium | Both candidates are retained; challenger was selected only after primary failed locked safety gates | Challenger gate regression -> restore logistic fallback or deterministic rules |
| R-03 | Action Window looks like a safety guarantee | Medium | High | Use interval language, “recommended within,” explicit basis and prototype disclaimer | Any “safe until” wording -> block release and correct all surfaces |
| R-04 | Rare critical cases are under-covered | Medium | High | Mondrian conformal calibration, cost sensitivity and stress tests | Coverage gate fails -> calibrated ensemble or conservative thresholds; increase review rate |
| R-05 | Alert burden overwhelms nurses | Medium | High | Consolidate alerts, suppress unchanged alerts, NBO specificity and two explicit denominators | Current TL-05 TriageLoop surge range is 0.86–1.12 alerts/waiting-patient-hour and 2.20–5.56 alerts/reassessment-nurse-hour; Community is the warning case. Nurse task testing failure -> tighten repeat suppression and use priority review queue (`artifacts/evaluation/tl-05-periodic-retriage-metrics.json`) |
| R-06 | Next Best Observation is not safe as a reassessment replacement | High | High | TL-05 gate failed: retain it only as a first-step suggestion and show the full-reassessment/escalation fallback | Any efficiency or clearance wording -> block release; do not promote an adaptively tuned bundle without new independent validation |
| R-07 | Queue optimisation starves lower-acuity patients | Low | High | Absolute deadline aging, category bounds and low-acuity P90 guardrail | Guardrail currently passes; regression -> add explicit fairness constraint and rerun |
| R-08 | 3x surge causes infeasible simulation or unstable policy | Low | Medium | Seeded custom event engine, capacity checks and three profiles | Reproducibility failure -> deterministic ETA fallback |
| R-09 | Paediatric/geriatric behaviour silently inherits adult thresholds | Low | High | Separate rule paths, explicit age bands and mandatory scenario tests | Any cross-band rule leak -> fail build until corrected |
| R-10 | Missing/OOD cases receive confident output | Medium | High | Data-quality scoring, plausibility, OOD and Safe Mode fixtures | Safe Mode gate fails -> block model recommendation and use deterministic fallback |
| R-11 | Clinician override becomes cosmetic | Low | High | Persist reason, prior/current state, actor, timestamp and downstream recomputation | Audit/override E2E fails -> block milestone completion |
| R-12 | Audit claims exceed prototype integrity | Low | Medium | Describe hash chain as immutable-style integrity aid, not production immutability | Wording review flags overclaim -> revise package |
| R-13 | Frontend/backend integration consumes schedule | Medium | Medium | Versioned contracts, thin vertical slice and early health endpoints | >90 minutes blocked -> switch SSE to polling; if needed use React/local or Streamlit fallback |
| R-14 | External-data access delays or is mistaken for validation | Medium | High | Isolate the open MIMIC-IV demo plausibility check; state that it is a 100-patient hospital/ICU demo, not ED validation | Credentialed MIMIC-IV-ED unavailable -> retain bounded input-scale check only and prohibit performance claims |
| R-15 | Public deployment is unreliable | Medium | Medium | Docker/local one-command path remains authoritative; verify clean setup | Hosting failure -> reproducible local demo and recorded evidence |
| R-16 | Competition requirement is implemented but not visible | Medium | High | Requirement-to-artifact/test traceability and scripted demo | Any uncovered row -> add visible evidence before submission |
| R-17 | Metrics encourage gaming or selective reporting | Low | High | Predeclared protocol, paired seeds, confidence intervals and all-cell reporting | Gate fails -> disclose, investigate and activate fallback; never delete unfavourable cells |
| R-18 | India privacy/regulatory language becomes inaccurate | Medium | Medium | Use official sources and label prototype controls versus legal compliance | Material rule change or uncertainty -> re-verify official sources before proposal release |
| R-19 | Two-week schedule slips | Medium | High | End-of-week vertical slice; 90-minute technical timebox; optional features ranked first to cut | Milestone slips -> drop optional MIMIC/public deployment/polish, activate component fallbacks |
| R-20 | Jury sees a feature bundle rather than one invention | Medium | High | Maintain one narrative: risk -> time -> capacity -> targeted observation -> clinician action | Story becomes diffuse -> remove non-core feature from main demo and move to appendix |
| R-21 | Stress probabilities look more certain than warranted | High | High | Publish stress ECE, OOD state and Safe Mode; do not interpret shifted probabilities as absolute clinical risk | Stress/OOD detected -> deterministic fallback and prospective local recalibration requirement |
| R-22 | Model learns workflow proxy instead of patient trajectory | Medium | High | Time-sliced leakage tests, patient-level splits and feature review; observation-count proxy removed | Proxy feature dominates importance -> remove it, retrain and rerun all locked gates |
| R-23 | Queue result depends on an arbitrary response-window definition | High | High | Separate hard-red-flag bound from composite escalation allowance and publish comparator-specific 10/20/30-minute sensitivity | Against periodic re-triage, improvement is 12.8%/13.0%/24.1%; only 30 minutes exceeds 20% -> prohibit universal “20%+” impact claim and require a local clinical definition |

## Release blockers

The following risks cannot be accepted for a milestone release:

- autonomous downgrade or suppressed hard red flag;
- missing uncertainty state;
- Safe Mode failure on registered fixtures;
- paediatric/adult rule leakage;
- unlogged clinician decision;
- unsupported clinical/impact claim;
- broken hero journey or irreproducible evaluation.
