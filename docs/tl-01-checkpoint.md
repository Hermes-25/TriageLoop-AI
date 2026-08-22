# TL-01 Data Checkpoint

Status: **Approved; TL-02 launched**  
Completed: 21 August 2026, 22:10 IST

## Outcome

The data and deterministic safety foundation is implemented and reproducible. No predictive model has been built early; TL-02 can now train against a clean temporal contract and hidden horizon labels.

## Delivered

- strict Pydantic patient/trajectory, quality, safety and synthetic-truth contracts;
- age-aware rule gate with hard flags, urgent review, worsening-vital and elapsed-wait events;
- Safe Mode for missing, stale, implausible and internally inconsistent observations;
- explicit no-autonomous-downgrade behavior;
- seeded longitudinal generator for 10,000 encounters;
- 28 curated named cases covering ambiguity, under-reporting, age groups, zero history, poor data, waiting deterioration and human-override candidates;
- generator configuration, data dictionary, rule catalogue and local reproduction command;
- 18 automated contract, safety, scenario and generator tests.

## Realized population

| Measure | Result |
|---|---:|
| Total encounters | 10,000 |
| Train / validation / test / stress | 5,700 / 1,900 / 1,900 / 500 |
| No / partial / available history | 5,079 / 1,986 / 2,935 |
| Stable / recovery / noisy | 5,506 / 1,110 / 1,112 |
| Slow / rapid deterioration | 1,482 / 790 |
| Curated cases | 28 |
| Automated tests | 18 passing |

## Exit-gate result

- Reproducibility: passed.
- Required age and history cohorts: passed.
- Required edge-case tags: passed.
- Contract validation and temporal ordering: passed.
- Rule precedence, worsening/wait recall and Safe Mode: passed.
- No autonomous downgrade across all curated cases: passed.

## Honest limitation

The generator encodes prototype assumptions and produces development evidence, not clinical evidence. Rule thresholds require licensed clinical governance and local validation before any real-world use. External datasets remain optional sanity checks rather than a dependency.

## Next controlled launch

`APPROVE TL-01 — START TL-02 MODEL`
