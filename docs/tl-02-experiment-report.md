# TL-02 Experiment Report

## Question

Can trajectory-aware calibrated prediction meet the predeclared recall, calibration and uncertainty gates while remaining subordinate to deterministic safety rules?

## Experimental design

- Patient-level seeded splits and time-indexed snapshots.
- Same features and label horizons for logistic primary and boosted challenger.
- Probability calibration isolated from training.
- Threshold/conformal selection isolated within validation.
- Test and deliberate distribution-shift cohorts evaluated only after the pipeline and gates were encoded.
- Cost settings retained at 5:1, 10:1 and 20:1; 10:1 selected as the prototype operating point.
- Conformal alpha swept at 0.05, 0.10 and 0.15; 0.10 selected before product integration.

## Result

The boosted challenger is selected by a safety-gate override. Logistic has slightly better mean probability error, but misses registered short-horizon/stress criteria after removal of a workflow-proxy feature. Boosting clears every registered horizon-level recall, test-ECE and critical-coverage gate.

At 30 minutes, conformal alpha 0.05/0.10/0.15 yields test ambiguity-review rates of 0.437/0.391/0.318 while preserving observed critical coverage of 0.975 in this synthetic test set. The 0.10 setting is the balanced prototype choice; the flat critical result is dataset-specific and not a general guarantee.

## Product translation

1. Rules and quality checks execute first.
2. Four calibrated horizon risks form a non-decreasing trajectory.
3. The earliest threshold crossing constrains the Action Window.
4. Category bounds can shorten, never lengthen, that window.
5. OOD or poor data invokes Safe Mode.
6. Ambiguity produces one ranked low-burden observation; near-term material ambiguity invokes Safe Mode.
7. Local stump contributions explain why estimated urgency moved.

## Negative and incomplete evidence

- Stress calibration is weak even though stress recall is high; OOD/Safe Mode is necessary and external calibration remains future work.
- The 30-minute operating point intentionally marks roughly 54.5% of test snapshots for model-positive review. Alert consolidation and queue simulation must determine whether this workload is operationally acceptable.
- Next Best Observation is implemented, but its 25%-fewer-observations/no-recall-loss gate requires counterfactual acquisition experiments in TL-05.
- Queue/Clinical Slack outcomes are intentionally not claimed before TL-03.

Machine-readable evidence: `artifacts/evaluation/tl-02-metrics.json`.
