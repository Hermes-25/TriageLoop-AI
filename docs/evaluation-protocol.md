# Predeclared Evaluation Protocol

Status: locked before model/data implementation to reduce metric cherry-picking.

## 1. Research questions

1. Does TriageLoop reduce missed action windows for time-critical simulated patients compared with FIFO and static five-level triage?
2. Does it reduce time to reassessment/escalation during crowding without producing unacceptable tail waits for lower-acuity patients?
3. Does uncertainty-aware escalation reduce unsafe under-triage while keeping clinician-review workload bounded?
4. Does Next Best Observation resolve decision uncertainty with fewer acquired observations than a fixed reassessment bundle?
5. Does performance remain directionally stable across age groups, history availability, site sizes and distribution-shift stress tests?

## 2. Policies compared

- **P0 - FIFO:** arrival order, except immutable immediate red flags.
- **P1 - Static triage:** generic five-level priority followed by arrival time within level.
- **P1b - Static + periodic re-triage (TL-05):** the same five-level policy, with new waiting-room observations reviewed at the next fixed 15-minute reassessment sweep and the deterministic five-level/rule logic reapplied. It does not use learned trajectory risk, conformal uncertainty, Action Windows or Clinical Slack.
- **P2 - TriageLoop:** hard rules, Dynamic Action Window, Clinical Slack, uncertainty escalation, waiting-time aging and Next Best Observation.

All policies replay the same patient arrivals, trajectories, service times and resource availability for paired comparison. P1b is the stronger TL-05 comparator: it separates the value of continuous model-informed prioritisation from the simpler value of periodically looking again.

## 3. Data splits

- Development/train: 60% of synthetic encounters.
- Calibration: 20%, isolated from training and used for probability/conformal calibration and operating thresholds.
- Test: 20%, untouched until the evaluation pipeline is fixed.
- Shift/stress set: separately generated changes in age mix, missingness, arrival load, symptom prevalence and measurement noise.
- Splits are patient-level and deterministic from the registered random seed.

## 4. Simulation matrix

- Site profiles: approximately 100, 300 and 500+ visits/day.
- Load states: baseline and 3x surge.
- Policies: FIFO, static triage and TriageLoop.
- Minimum repetitions: 100 seeded shifts for each site x load x policy cell.
- Report paired differences with bootstrap 95% intervals across shift repetitions.

## 5. Primary safety/operational endpoints

1. Action Window miss rate among time-critical patients.
2. Unsafe under-triage rate.
3. Time from deterioration signal to reassessment/escalation.
4. Critical-case recall.
5. Minutes of negative Clinical Slack.

## 6. Secondary endpoints

- Waiting-Time Triage Effectiveness and Rank-based Triage Effectiveness.
- Median and 90th-percentile wait by acuity.
- Throughput, queue length and resource utilisation.
- Conformal empirical coverage by critical/non-critical class.
- Calibration error and Brier score by horizon.
- Abstention/review rate and alerts per waiting-patient hour.
- Consolidated alerts per reassessment-nurse hour, with site/load-specific reporting and no assumed “safe” workload threshold.
- Number and burden of observations requested.
- Override rate, acknowledgement time and override reasons.
- Performance gaps by paediatric/adult/geriatric group and prior-history availability.

## 7. Predeclared prototype gates

These are build acceptance gates on synthetic/simulated evaluation, not clinical claims:

- Critical-case recall: at least 0.90 in-distribution and 0.85 on the stress set.
- Critical-class empirical conformal coverage: at least the selected nominal target minus 0.03.
- Expected calibration error: no more than 0.08 at the selected operating horizon.
- 3x-surge Action Window miss rate: at least 20% relative reduction versus static triage.
- Low-acuity 90th-percentile wait: no more than 20% worse than static triage unless the difference is explicitly explained by a safety trade-off.
- Next Best Observation: at least 25% fewer acquired observations than the fixed bundle with no material loss of critical recall.
- Safe Mode: 100% activation for registered hard failure fixtures.
- Required scenario tests: 100% pass.

If a gate fails, report the failure transparently, activate the relevant fallback and rerun. Never change the gate after viewing final test results without recording the decision.

### TL-05 outcome record

- The P1b comparison passed its directional and low-acuity guardrail checks: 20.5% fewer 3×-surge Action Window misses versus fixed 15-minute periodic re-triage (95% CI 17.4%–23.8%). This was an added stronger-comparator interpretation gate, not a retroactive change to the original P1 gate.
- The single-observation NBO gate failed: 87.5% fewer observations with a 7.1 percentage-point operational critical-recall loss versus the fixed bundle. The full-reassessment/escalation fallback is active.

## 8. Model selection rule

- Primary candidate: discrete-time logistic hazard model.
- Challenger: gradient-boosted discrete-time hazard model.
- Select the challenger only if it materially improves critical recall/calibration or Action Window performance across test and stress sets without unacceptable subgroup or explanation burden.
- AUROC alone cannot select the final model.

## 9. Threshold/cost analysis

- Evaluate under-triage:over-triage cost ratios of 5:1, 10:1 and 20:1.
- Sweep conformal nominal coverage and report coverage-efficiency-review-workload trade-offs.
- Choose the operating point on the calibration split before final test evaluation.

## 10. Reproducibility and reporting

- Version the generator, data schema, rule set, model, configuration and random seed.
- Save machine-readable metrics and a human-readable evaluation report.
- Label every figure/table as synthetic, simulated or externally sourced.
- Publish negative, neutral and positive results; do not report only favourable site/load cells.
