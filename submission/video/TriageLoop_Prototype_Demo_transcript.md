# TriageLoop Prototype Demo Transcript

This transcript mirrors the burned-in captions in the 2:05 release-candidate video.

**00:00–00:07 — Opening**  
TriageLoop. Patient need becomes time. Time is tested against capacity. A clinician closes the loop. Synthetic decision-support prototype; not validated for clinical use.

**00:07–00:16 — Living Acuity**  
The queue is continuously re-ranked by clinical level, Action Window and Clinical Slack—not arrival time alone.

**00:16–00:29 — Deterioration and Clinical Slack**  
A new observation is evaluated immediately: rules first, then calibrated trajectory risk and uncertainty. P-0009 moves to position 2. The Action Window is now; predicted action is eight minutes away; Slack is minus eight minutes.

**00:29–00:39 — Explainability and hard rules**  
Observed oxygen, respiratory-rate and heart-rate changes are shown. A hard red flag cannot be relaxed by the model.

**00:39–00:50 — Next Best Observation**  
Repeat SpO₂ is the first useful measurement—not a substitute for full reassessment when uncertainty persists.

**00:50–01:02 — Queue Twin**  
Under three-times demand, clinical need does not move. TriageLoop exposes infeasible deadlines instead of manufacturing reassurance.

**01:02–01:19 — Clinician authority**  
Accept, modify or override remain human decisions. An override requires a reason tied to the exact recommendation.

**01:19–01:30 — Auditable loop**  
Observation, queue reorder and clinician response are append-only and recomputed through a SHA-256 integrity chain.

**01:30–01:53 — Evidence and limits**  
Across 1,200 synthetic paired shifts, TriageLoop produced 20.5% fewer surge misses versus fixed 15-minute periodic re-triage. Response sensitivity is disclosed, the single-observation NBO gate failed, and no clinical-validation claim is made.

**01:53–02:05 — Close**  
Know who is becoming unsafe to wait—and whether the emergency department can act in time. Rules first. Uncertainty visible. Capacity honest. Clinician in control.

