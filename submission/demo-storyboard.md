# TriageLoop Prototype Demo Storyboard

Final delivered recording: `video/Zeta_Prototype.mp4` (**4:43**, 2560 × 1440, 30 fps, narrated). The timing tables below are retained as the production storyboard and claim-control guide; the approved final recording supersedes their provisional cut lengths.

## Full cut

| Time | Screen/action | Spoken line | Proof shown |
|---:|---|---|---|
| 0:00-0:20 | Title over the live board | “A triage category is captured once. The patient and the queue keep changing. TriageLoop identifies who is becoming unsafe to wait, by when action is needed, and whether the ED can actually meet that need.” | Problem and proposition |
| 0:20-0:45 | Reset demo; select P-0009 in baseline | “This is a working nurse-facing Deadline Board. Twenty pseudonymous patients, drawn from a 28-case test library, are ranked by clinical level, Action Window and Clinical Slack - the time remaining after the predicted next action.” | Working product, synthetic boundary |
| 0:45-1:25 | Run deterioration event | “P-0009’s SpO2 falls to 88%, respiratory rate rises to 37 and heart rate rises. Rules run first. The patient moves to position two, the Action Window becomes ‘now,’ predicted action is eight minutes away, and Slack becomes minus eight.” | Continuous monitoring, worsening-vital trigger, queue reorder, negative Slack |
| 1:25-1:55 | Inspect why/trajectory/Slack | “The system does not hide the capacity failure or describe the patient as safe. It shows what changed, which factors were used, the calibrated horizons and the hard rules that the model cannot relax.” | Explainability, uncertainty, rules-first safety |
| 1:55-2:25 | Select P-0012; show NBO | “Where uncertainty matters, TriageLoop can suggest the first useful observation - here, repeat SpO2. Our verification found that one observation cannot replace a full reassessment, so the product says that explicitly and escalates when uncertainty persists.” | Honest failed NBO gate and fallback |
| 2:25-2:55 | Switch to 3x surge/Capacity | “Under 3x demand the clinical requirement does not move. More deadlines become infeasible, so the charge nurse sees the operational conflict instead of a falsely relaxed priority.” | Surge behavior, scalability, capacity truth |
| 2:55-3:25 | Return P-0009; override with reason | “The nurse remains accountable. Accept, modify and override are available. An override requires a reason and is recorded against the exact recommendation.” | Human authority and override |
| 3:25-3:45 | Open Audit | “The audit view recomputes every SHA-256 event hash and link. It records the observation, queue reorder and clinician response; it does not claim production immutability.” | Tamper-evident audit |
| 3:45-4:10 | Open Evidence; point to response sensitivity | “Across 1,200 paired verification shifts, TriageLoop reduced synthetic surge Action Window misses by 20.5% versus fixed 15-minute periodic re-triage. A post-verification sensitivity run produced 12.8%, 13.0% and 24.1% reductions at 10, 20 and 30 minutes—so only the 30-minute definition exceeded 20%. The interface also shows the NBO failure and external-data limitation.” | Stronger comparator, quantified sensitivity, negative evidence, claim control |
| 4:10-4:30 | Return board/closing slate | “TriageLoop turns changing patient need into an actionable deadline, tests that deadline against real capacity, and keeps the clinician in control. When the department cannot act in time, the system says so early enough to respond.” | Final jury proposition |

## Contingency cut

Use 0:00-0:20, 0:45-1:55, 2:55-3:45 and 3:45-4:30. Compress evidence narration to: “Against fixed 15-minute periodic re-triage, the synthetic surge miss rate fell 20.5%; the NBO recall gate failed and remains visibly constrained.”

## Recording controls

- Begin from `POST /v1/demo/reset`; verify the baseline banner before recording.
- Keep the synthetic/not-clinically-validated notice visible whenever possible.
- Do not state that the displayed rules or Action Windows are clinically validated.
- Do not claim NBO saves nurse time; call it a first-measurement suggestion.
- If the live service fails, stop recording. Do not use stale ETA/Slack as if current.
- Capture system audio separately only if it improves clarity; avoid background music over clinical narration.
- Keep the six captured product-surface references in `submission/visuals/product-surfaces/` beside the recording package; they cover the board, override, audit, evidence, capacity and degraded-mode views.
