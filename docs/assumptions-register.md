# Assumptions Register

Status: locked for TL-00 approval  
Owner: TriageLoop project team  
Review authority: Abhishek Das

## A. Intended use and users

- TriageLoop is a research prototype for nurse-facing emergency-department decision support.
- Primary user: triage/waiting-room nurse.
- Secondary users: charge nurse, ED operations lead and prototype administrator/evaluator.
- It recommends reassessment, escalation priority and queue/resource attention. It does not diagnose, prescribe, discharge or autonomously downgrade.
- A licensed clinician remains accountable for every patient-level action.

## B. Care setting

- Facility-based emergency departments ranging from approximately 100 to 500+ visits/day.
- Three configurable prototype profiles: community (100/day), regional (300/day) and urban/trauma-scale (500+/day).
- Workload scenarios: baseline, busy and 3x surge.
- Approximately half of arriving patients have some prior-record context and half are zero-history/first-time patients.
- Prototype resource types: triage nurse, reassessment nurse, clinician, monitored space and treatment space.

## C. Patient groups

- Paediatric: younger than 12 years, aligned with the WHO IITT separation used in the research basis.
- Adult: 12-64 years.
- Geriatric: 65 years and older, using adult emergency rules plus explicit frailty, comorbidity and atypical-presentation context.
- Model evaluation and safety reporting are stratified across these groups and by prior-history availability.

## D. Baseline triage representation

- Use a generic five-level severity scale for the static-triage comparator.
- Do not claim implementation or validation of a proprietary/local hospital triage protocol.
- Existing category-level maximum waits are treated as upper bounds; TriageLoop may recommend earlier action but never an autonomous downgrade or extension beyond the bound.
- Hard red flags override model output and immediately recommend clinician review/escalation.

## E. Prediction target

- Primary model target: simulated need for urgent clinical escalation within 5, 15, 30 or 60 minutes.
- The simulated deterioration composite may include resuscitation-level vital abnormality, urgent senior review, monitored-care requirement or treatment-space escalation.
- It is not “time to death” and is never described as such.
- The target is generated from documented scenario mechanisms and is used to demonstrate the operating model, not clinical effectiveness.

## F. Dynamic Action Window

- The Action Window is a conservative interval by which the next specified action should occur.
- It is derived from the earliest of: a hard-rule trigger, the severity-category maximum wait, or the earliest calibrated prediction horizon crossing an escalation threshold.
- The interface uses “recommended within” or a bounded interval, never “safe until.”
- A model-derived window cannot cancel or lengthen a hard-rule requirement.

## G. Error asymmetry and uncertainty

- Missing a critical patient is categorically more costly than unnecessary reassessment.
- Experiments will report sensitivity analyses at under-triage:over-triage cost ratios of 5:1, 10:1 and 20:1 rather than hiding the trade-off inside one arbitrary setting.
- Primary operating selection prioritizes critical-class recall and empirical critical-class coverage, subject to a bounded alert/review workload.
- Ambiguous conformal sets, material missingness or OOD conditions trigger review/escalation; they do not trigger automatic downgrading.

## H. Next Best Observation

- Candidate actions are restricted to a clinician-approved prototype catalogue of low-burden observations and history questions.
- Examples: repeat SpO2, respiratory rate, heart rate, blood pressure, temperature, mental-status check, pain reassessment and symptom-onset clarification.
- No autonomous medication, treatment, laboratory or imaging order is generated.
- Recommendations balance expected decision impact against acquisition time and burden.
- TL-05 showed that one suggested observation does not preserve operational critical recall within the predeclared boundary. NBO is consequently first-step guidance only; full reassessment or escalation is the safe fallback.

## I. Data

- Approximately 10,000 reproducible synthetic longitudinal encounters support development and simulation.
- 24-30 curated cases support human-readable demonstrations and automated scenarios.
- Synthetic generation is documented, seeded and separated into development, calibration, test and distribution-shift sets.
- The open MIMIC-IV Clinical Demo is used only for a non-critical-path adult hospital/ICU input-scale sanity check. Credentialed MIMIC-IV-ED remains unavailable and no external performance claim is made.
- No identifiable or real patient data is required or permitted in the prototype.

## J. Jurisdiction, privacy and governance

- Assumed jurisdiction: India.
- Governance framing: DPDP Act 2023 and its phased 2025 Rules, ABDM Health Data Management Policy and Indian EHR Standards. Under the 13 November 2025 commencement notification, Rules 1, 2 and 17-21 commenced immediately; Rule 4 commences after one year; Rules 3, 5-16, 22 and 23 commence after 18 months, on 13 May 2027.
- Prototype principles: synthetic/pseudonymous identifiers, data minimisation, purpose limitation, role-based views, explicit audit events, configurable retention and no secondary data use.
- The role selector is a workflow demonstration, not production authentication or authorization.
- The prototype is designed toward the full governance baseline now; this is not a claim of legal compliance, certification or a substitute for deployment-specific counsel.

## K. Evaluation claims

- All reported numbers are prototype results from synthetic data and/or simulation unless explicitly labelled otherwise.
- Predeclared acceptance gates are targets, not achieved outcomes.
- No claim of clinical validation, patient safety improvement, hospital savings, production readiness, regulatory clearance, patent novelty or “world first.”

## L. Change control

An assumption change requires explicit approval if it alters patient safety, human accountability, the core operating model, problem-statement coverage or evaluation validity. Lower-level implementation changes may be made autonomously and recorded in the decision log.
