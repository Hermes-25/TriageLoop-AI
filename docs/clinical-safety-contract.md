# Clinical Safety Contract

This contract defines prototype behaviour that implementation may not violate.

## Safety invariants

1. **Rules before model:** age-aware red flags are evaluated before ML recommendations.
2. **No autonomous downgrade:** model output cannot lower a clinician-assigned category or suppress a hard-rule escalation.
3. **Uncertainty escalates attention:** ambiguous prediction sets, missing critical inputs, implausible observations or OOD states produce review or Safe Mode.
4. **Waiting patients remain active:** elapsed safe-wait thresholds and every new observation trigger reassessment of the patient's state.
5. **Action Window is bounded:** it cannot exceed the configured category maximum wait and is never presented as a safety guarantee.
6. **Queue pressure cannot redefine clinical need:** surge may alter predicted time-to-care and resource recommendations, but never relax a patient's clinical requirement.
7. **Human control is explicit:** every recommendation supports accept, modify and override.
8. **Audit is complete:** each recommendation records timestamp, patient state, input provenance/freshness, rule hits, model/version, uncertainty, Action Window, queue estimate, explanation and clinician response.
9. **Clinical truth is deterministic/model-based:** an LLM, if later used for text structuring or explanation, never calculates the clinical score, hazard, Action Window or priority.
10. **Prototype limitation is visible:** every clinical screen states that the system is simulated decision support and not validated for clinical use.
11. **Compound triggers resolve once:** when Safe Mode, hard rules, model disagreement or waiting thresholds co-occur, present one most-conservative action and list every contributing reason. A model result may never compete visually with or relax the rule outcome.
12. **NBO is never sufficient clearance:** Next Best Observation may identify the first useful measurement, but cannot replace a full reassessment, justify delay or clear a critical concern. Unavailable measurement, persistent uncertainty or concern requires the full bundle or escalation.

## Safe Mode triggers

- Missing critical age-specific input required for rule evaluation.
- Implausible or internally inconsistent vital signs.
- Observation staleness beyond the configured threshold.
- OOD score above the calibrated limit.
- Model artifact missing, incompatible or unhealthy.
- Conformal prediction set remains materially ambiguous for a safety-critical decision.
- Simulation/queue service unavailable when capacity feasibility is required.

## Safe Mode behaviour

- Preserve or increase the current priority; never automatically decrease it.
- Fall back to age-aware deterministic rules and the fixed category deadline.
- Recommend clinician reassessment with a specific reason.
- Mark queue feasibility as unknown when it cannot be calculated.
- Record the trigger and fallback pathway in the audit trail.
- If the calculation service is unavailable, retain the last verified state only as historical context, mark live trajectory/ETA/Slack unavailable, disable digital state-changing actions and direct staff to the local downtime record and escalation protocol.

## Explanation contract

Every recommendation must answer, in one nurse-readable view:

- What action is recommended?
- By when?
- What changed?
- Which observations/rules contributed most?
- How reliable is the recommendation?
- What should be measured next if uncertainty matters?
- What will be recorded if the clinician accepts, modifies or overrides?

## Alert-control contract

- Consolidate multiple model/rule signals into one patient-level action.
- Do not repeat an unchanged low-priority alert.
- Escalate alert salience only when urgency, uncertainty or Clinical Slack materially worsens.
- Track alerts per waiting-patient hour, acknowledgement time, override rate and override reason.
