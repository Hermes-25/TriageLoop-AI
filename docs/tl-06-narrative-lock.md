# TL-06 Jury Narrative Lock

Date: 22 August 2026  
Status: controlling narrative for proposal, pitch, README and demo

## One-sentence proposition

TriageLoop continuously turns a waiting patient's changing condition into a conservative Action Window, checks whether the live ED queue can act in time, and makes any capacity shortfall visible as negative Clinical Slack while keeping every decision with the clinician.

## Opening tension

A conventional triage category is recorded at arrival. The patient and the queue continue to change. The operational failure is therefore not only “Who looks high risk?” but “Who is becoming unsafe to wait, by when must we act, and can the department actually meet that need?”

## Three-beat answer

1. **Patient need becomes time:** age-aware rules, calibrated trajectory risk and uncertainty create a bounded Action Window.
2. **Time meets capacity:** the Queue Twin projects the next clinical action; Action Window minus ETA becomes Clinical Slack.
3. **A clinician closes the loop:** deterioration triggers re-ranking; uncertainty triggers review; accept/modify/override decisions are reasoned and hash-audited.

## Defensible distinction

TriageLoop does not claim first use of AI triage, dynamic risk, queue ranking, conformal prediction, predictive maintenance or active feature acquisition. Its contribution is the safety-oriented recomposition of those ideas into one ED waiting-room control loop:

- risk is translated into a conservative action deadline rather than a score alone;
- queue capacity is tested against that deadline instead of silently redefining clinical need;
- uncertainty produces Safe Mode and a first-measurement suggestion, never autonomous clearance;
- age-aware rules can promote urgency and can never be relaxed by the model;
- clinician action and the exact recommendation are linked in a tamper-evident audit stream.

## Lead evidence

- 1,200 TL-05 verification policy shifts: two policies × three site profiles × baseline/3x load × 100 replications. This is distinct from the earlier 1,800-shift, three-policy TL-03 matrix.
- Under 3x surge, 17.7% to 14.1% Action Window miss rate versus fixed 15-minute periodic re-triage: 20.5% relative reduction, 95% CI 17.4%-23.8%.
- 14.0% fewer negative-Slack minutes, 15.7% faster signal-to-action and 14.4% lower low-acuity P90 wait versus the same stronger comparator.
- Post-verification periodic-comparator sensitivity: 12.8%/13.0%/24.1% fewer misses at 10/20/30 minutes; only 30 minutes exceeds 20%, so no universal “20%+” claim is permitted.
- 73 automated tests (71-test TL-05 baseline plus two TL-06.5 regressions), deterministic reruns, working outage behavior and recomputed audit integrity.

## Credibility moment

The single-observation Next Best Observation hypothesis failed its predeclared recall-preservation gate: it requested 87.5% fewer observations but lost 7.1 percentage points of operational critical recall. It remains a first measurement suggestion only. Full reassessment or escalation is the locked fallback. This negative result must appear in the proposal, deck and evidence view.

## Business framing

TriageLoop is not sold as a substitute for staffing or a clinically validated device. It is proposed as a configurable decision-support and operational-risk layer for ED waiting rooms. A hospital pilot must earn expansion through local retrospective validation, shadow-mode safety gates, nurse usability, alert burden, Action Window adherence and governance approval.

## Jury close

When capacity is constrained, TriageLoop does not create false reassurance. It shows exactly where clinical need and operational reality have diverged - early enough for a clinician and charge nurse to act.

## Prohibited claims

- clinical validation, patient-safety improvement or hospital savings already achieved;
- production readiness, regulatory approval or legal compliance;
- autonomous diagnosis, treatment, discharge, ordering or triage downgrade;
- “world first,” patent novelty or first AI/dynamic triage system;
- NBO workload reduction without new independent evidence;
- a minute-level guarantee that a patient is safe until a deadline.
