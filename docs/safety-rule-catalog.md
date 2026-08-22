# Prototype Safety Rule Catalogue

These rules exist to demonstrate deterministic precedence, age awareness and failure behavior. They are conservative prototype assumptions, not a validated triage protocol and not for clinical use.

| Rule family | Prototype trigger examples | Behavior |
|---|---|---|
| Hard red flag | SpO2 below 90%, GCS at/below 8, severe responsiveness impairment, extreme age-adjusted vital, stridor/cyanosis/seizure/uncontrolled bleeding/stroke cue | Recommend level 1 review/escalation |
| Urgent review | SpO2 90–93%, GCS below 15, confusion, severe pain, high geriatric frailty | Recommend at least level 2 review |
| Worsening trajectory | material SpO2, respiratory-rate, pressure or GCS deterioration between the latest two readings | Recall waiting patient; recommend at least level 2 |
| Wait bound | clinician category maximum wait reached | Reassessment due; move recommendation only toward greater urgency |
| Data quality | missing critical vital, broad-range implausibility, inconsistent BP or observation older than 30 minutes | Safe Mode and named reassessment reason |

## Age behavior

- Paediatric patients use prototype age-banded heart-rate, respiratory-rate and hypotension extremes.
- Adults use adult extremes.
- Geriatric patients use adult extremes plus explicit frailty and atypical/confusion review cues.

## Invariants

Rules execute before the future model; the most urgent applicable result wins; the nurse-assigned level is the least-urgent permissible output; and any quality failure preserves or increases attention.
