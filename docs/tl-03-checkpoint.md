# TL-03 Queue Checkpoint

Status: **Ready for executive approval**
Completed: 22 August 2026, 06:55 IST

## Delivered

- three configurable 100/300/550-visits-day site profiles;
- explicit triage, reassessment, clinician, monitored-space and treatment-space capacity;
- FIFO, static five-level and TriageLoop scheduling policies;
- product-facing ETA, Clinical Slack and capacity-conflict contract;
- deterioration, uncertainty and waiting-time reordering logic;
- baseline and 3× surge experiments with 100 paired replications per cell;
- paired bootstrap confidence intervals and response-window sensitivity;
- bounded eight-item low-burden observation catalogue;
- simulation card, machine-readable evidence and 45 automated tests.

## Gate status

- 1,800 registered policy shifts completed: passed.
- Registered synthetic 3× miss-rate relative reduction at the 30-minute composite response definition: passed at 36.0% (31.2%–41.1% CI). The result does not clear the 20% gate at the stricter 10-minute definition.
- Each site’s surge point estimate >=20%: passed; community interval is less conclusive.
- Low-acuity guardrail: P90 wait must not be more than 20% worse — passed.
- Observed result: low-acuity P90 wait improved by 57.0% overall in the registered synthetic comparison.
- Negative Slack and signal-to-action improvements: passed.
- Negative-slack patient exposed by contract test: passed.
- Deterministic scenario reordering from deterioration, uncertainty, elapsed deadline and capacity: passed.
- Repeated full-matrix metrics and shift hashes: passed.

## Executive interpretation

Approve the Queue Twin and TriageLoop policy as the operational prototype baseline. The patient-first claim is that a new observation can reveal a person becoming unsafe to continue waiting; the Queue Twin then exposes whether the current ED can meet that changed need. The Community 3× case remains unsafe in absolute terms and shows that software cannot substitute for capacity.

## Next controlled launch

`APPROVE TL-03 — START TL-04 PRODUCT`
