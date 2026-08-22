# TriageLoop TL-02 Model Card

Status: synthetic research prototype; not clinically validated and not for clinical use.  
Model version: `2.0.0`

## Intended use

Estimate simulated need for urgent escalation within 5, 15, 30 and 60 minutes for a patient already in an ED triage/waiting workflow. Outputs support a nurse-facing Dynamic Action Window and uncertainty-aware reassessment. They do not diagnose, prescribe, discharge or autonomously downgrade.

## Data and leakage controls

- 10,000 seeded synthetic encounters; 30,020 time-indexed snapshots.
- Patient-level allocation: 17,114 train, 5,685 validation, 5,708 untouched test and 1,513 deliberate stress snapshots.
- Validation encounters are deterministically divided between probability calibration and conformal/threshold selection.
- A snapshot uses only observations recorded at or before its prediction time. Hidden event labels and future observations are excluded from features.
- “Number of observations” was removed after audit because it could proxy workflow intensity rather than physiology.

## Candidates and selection

The primary benchmark is L2-regularised discrete-time logistic hazard. The challenger is a compact gradient-boosted ensemble of logistic decision stumps. Both receive the same 44 standardised/imputed features and Platt calibration.

The boosted challenger is selected because it passes all registered horizon-level safety gates while logistic does not. Logistic remains the transparent fallback.

| Comparison | Logistic | Boosted |
|---|---:|---:|
| Mean test recall | 0.928 | 0.935 |
| Mean stress recall | 0.862 | 0.941 |
| Mean test Brier | 0.0476 | 0.0498 |
| All registered TL-02 safety gates | Fail | Pass |

## Selected-model results

All results below are synthetic prototype evidence.

| Horizon | Test recall | Stress recall | Test ECE | Test critical conformal coverage | Stress critical conformal coverage | Test threshold-positive rate |
|---:|---:|---:|---:|---:|---:|---:|
| 5 min | 0.914 | 0.891 | 0.003 | 0.973 | 0.977 | 0.080 |
| 15 min | 0.902 | 0.923 | 0.008 | 0.902 | 0.923 | 0.267 |
| 30 min | 0.975 | 0.982 | 0.016 | 0.975 | 0.982 | 0.545 |
| 60 min | 0.949 | 0.968 | 0.026 | 0.949 | 0.968 | 0.523 |

Operating thresholds are selected on validation data at the registered 10:1 under-triage:over-triage cost setting subject to at least 0.90 validation recall: 0.4100, 0.0393, 0.0600 and 0.1225 for 5/15/30/60 minutes respectively. The low 15/30-minute thresholds make the intended asymmetric safety trade-off visible rather than hiding it.

## Subgroups

At 30 minutes on the test set:

- paediatric/adult/geriatric recall: 0.963 / 0.969 / 0.991;
- no/partial/available-history recall: 0.975 / 0.978 / 0.971;
- worst-to-best observed subgroup recall range: 0.028.

These checks do not establish fairness or clinical generalisability; the cohorts inherit generator assumptions.

## Uncertainty and shift

- Platt calibration produces horizon probabilities.
- 90% nominal Mondrian prediction sets provide separate critical/non-critical error control.
- Feature-space OOD detection flags 1.1% of test snapshots and 18.2% of stress snapshots for Safe Mode.
- Stress ECE rises materially (0.078–0.266). Stress recall remains high, but the probabilities must not be interpreted as calibrated absolute clinical risks under shift. Safe Mode and prospective local recalibration are required.

## Explainability

The selected ensemble contains shallow decision stumps. Each recommendation aggregates the active stump contributions into local nurse-readable factors. Globally, the strongest synthetic signals are confusion, current and changing SpO2, clinician-assigned level, and changes in respiratory rate and heart rate.

## Safety integration

Deterministic age-aware rules execute first. The Action Window is the earliest of hard-rule action, fixed category bound and calibrated hazard crossing. Missing/stale/implausible data, OOD state or material near-term ambiguity activates Safe Mode. Model output cannot extend a rule/category bound or permit autonomous downgrade.

The TL-05 counterfactual test did **not** qualify a single Next Best Observation as a replacement for full reassessment: it reduced requested measurements by 87.5% but lowered operational critical recall by 7.1 percentage points versus the fixed eight-observation bundle, exceeding the predeclared 2-point limit. The UI may therefore show NBO only as the first suggested measurement. If it is unavailable, uncertainty persists or concern remains, the required fallback is full reassessment or escalation. No NBO efficiency/safety claim is permitted.

## Limitations

- Entirely synthetic development evidence; no patient outcome claim.
- Labels and deterioration mechanisms reflect the generator design.
- Text cues are simple deterministic indicators, not validated clinical language understanding.
- Next Best Observation remains a bounded first-step heuristic after failing its TL-05 recall-preservation gate; its acquisition times are catalogue assumptions rather than nurse time-and-motion evidence.
- Thresholds, calibration, rules and subgroup behavior require prospective clinical validation and local governance before real use.

## Reproduction

Seed: `20260821`. Selected-model SHA-256: `b37ab29077acd37865f3a9de89c070f37bbb549f8bc13f40d819146161a51990`. Repeated training produced identical model and metrics hashes.
