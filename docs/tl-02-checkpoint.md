# TL-02 Model Checkpoint

Status: **Approved; TL-03 launched**  
Completed: 22 August 2026, 05:57 IST

## Outcome

The trajectory-risk and uncertainty layer is implemented, selected by predeclared gates, serialized and connected to deterministic safety, Dynamic Action Window and Next Best Observation outputs.

## Delivered

- leakage-safe 44-feature longitudinal snapshot pipeline;
- logistic discrete-time hazard primary benchmark;
- compact gradient-boosted hazard challenger;
- Platt probability calibration at 5/15/30/60 minutes;
- 5:1, 10:1 and 20:1 threshold/cost analysis;
- 85%, 90% and 95% class-conditional conformal sensitivity analysis;
- feature-space OOD detector;
- Dynamic Action Window bounded by hard rules and category maximum waits;
- targeted low-burden Next Best Observation;
- versioned recommendation envelope and compact selected-model artifact;
- model card, full machine-readable metrics and 34 passing automated tests.

## Executive model decision

Approve the boosted challenger as the TL-02 selected prototype model and retain logistic as the interpretable fallback. The challenger is selected because it passes all locked safety gates; the primary does not. This is not an AUROC-only selection.

## Gate status

- Test recall >=0.90 at all four horizons: passed.
- Stress recall >=0.85 at all four horizons: passed.
- Test ECE <=0.08 at all four horizons: passed.
- Test and stress critical conformal coverage >=0.87: passed.
- Required age/history subgroup reporting: passed.
- Safe Mode/no-autonomous-downgrade scenarios: passed.
- Deterministic model and metrics hashes: passed.
- NBO counterfactual efficiency gate: deferred as predeclared to TL-05.
- Queue/3x-surge gates: scheduled for TL-03/TL-05.

## Known operational trade-off

The safety-biased 30-minute threshold-positive rate is 54.5% on the synthetic test snapshots. TL-03 must test whether Clinical Slack, alert consolidation and capacity-aware scheduling turn this sensitivity into usable workflow rather than alert burden.

## Next controlled launch

`APPROVE TL-02 — START TL-03 QUEUE`
