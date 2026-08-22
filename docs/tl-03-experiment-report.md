# TL-03 Queue Experiment Report

## Outcome

The registered Queue Twin matrix contains 1,800 policy-shift runs: three sites × two load states × three policies × 100 identical-seed replications. The overall 3×-surge Action Window gate and low-acuity tail guardrail pass.

## Critical Action Window miss rate under 3× surge

| Site | Static | TriageLoop | Relative reduction | Paired bootstrap 95% interval |
|---|---:|---:|---:|---:|
| Community | 0.325 | 0.257 | 20.8% | 13.9%–27.7% |
| Regional | 0.166 | 0.082 | 50.4% | 42.1%–59.0% |
| Urban/trauma | 0.167 | 0.082 | 51.2% | 45.7%–57.1% |
| Overall | 0.219 | 0.141 | 36.0% | 31.2%–41.1% |

The overall row is synthetic-system evidence from the registered 30-minute composite-response definition. Its comparator is initial five-level category plus arrival order and does not process later observations. The reduction is 11.1% at the strictest 10-minute definition tested and does not clear the 20% gate there; it is not evidence of clinical outcome benefit.

The community point estimate clears the gate, but its interval includes improvements below 20%. The overall paired interval remains above the gate.

## Capacity and starvation

| Site | Static low-acuity P90 | TriageLoop low-acuity P90 | TriageLoop critical recall | TriageLoop capacity-conflict rate | Alerts/waiting-patient-hour |
|---|---:|---:|---:|---:|---:|
| Community | 97.1 min | 42.4 min | 0.743 | 0.333 | 1.119 |
| Regional | 45.4 min | 19.2 min | 0.918 | 0.139 | 0.956 |
| Urban/trauma | 44.8 min | 19.0 min | 0.918 | 0.098 | 0.859 |

The low-acuity guardrail passes with substantial margin; TriageLoop does not obtain the critical-case improvement by starving levels 4–5. Clinician utilisation during surge is approximately 0.82–0.85, with monitored-space utilisation 0.74–0.86.

## Mechanism demonstrated

- Repeat observations can shorten a patient’s deadline and promote their dynamic level.
- Uncertainty breaks otherwise equal priority ties toward reassessment.
- Absolute category/model deadlines make Slack decline as a patient waits.
- Queue projection can turn a positive clinical window into negative Slack when capacity is inadequate.
- Capacity changes feasibility and alerting, not clinical need.

## Negative and incomplete evidence

- Under baseline capacity, all policies have zero critical misses; TriageLoop offers no measurable miss-rate gain there.
- The community 3× environment remains unsafe in absolute terms despite relative improvement.
- The 20% miss-reduction conclusion does not hold at the strictest 10-minute composite-response sensitivity setting.
- Rank and waiting-time effectiveness do not improve uniformly in every cell; the strongest evidence is deadline adherence, lateness and tail wait.
- This simulator is not calibrated to a real hospital and cannot justify staffing changes or patient-care claims.

Machine-readable evidence: `artifacts/evaluation/tl-03-queue-metrics.json` and `artifacts/evaluation/tl-03-shifts.jsonl`.
