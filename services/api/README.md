# Decision and Simulation API Boundary

Stack boundary: Python 3.12+, Pydantic runtime contracts, and FastAPI from the product phase onward.

Responsibilities:

- contract validation and ingestion;
- age-aware safety rules and plausibility;
- longitudinal feature state;
- discrete-time hazard prediction and calibration;
- conformal uncertainty and OOD/data quality;
- Dynamic Action Window;
- Clinical Slack and queue simulation;
- Next Best Observation;
- clinician decision persistence and audit;
- experiment orchestration and metrics.

The recommendation envelope must always return deterministic safety output even when a model or simulator is unavailable.

## Implemented in TL-01

- strict runtime patient, observation, truth and safety-result contracts;
- completeness, reliability, freshness and plausibility assessment;
- Safe Mode for missing, stale or implausible critical observations;
- paediatric/adult/geriatric deterministic rule evaluation;
- wait-threshold and worsening-trajectory reassessment triggers;
- seeded longitudinal generator and named edge-case catalogue.

The thresholds are conservative prototype rules for simulation—not a validated hospital protocol or clinical guidance.

## Implemented in TL-02

- leakage-safe time-indexed feature extraction;
- logistic and boosted discrete-time horizon models;
- Platt calibration and cost-sensitive operating thresholds;
- Mondrian conformal prediction sets and OOD detection;
- bounded Dynamic Action Window orchestration;
- local factor explanations and Next Best Observation;
- serialized selected-model bundle and reproducible evaluation evidence.

## Implemented in TL-03

- configurable community/regional/urban-trauma resource profiles;
- minute-resolution triage, reassessment, clinician and space simulation;
- FIFO, static five-level and TriageLoop policies on identical shifts;
- queue ETA, Clinical Slack and capacity-conflict snapshots;
- dynamic reordering from deterioration, uncertainty and elapsed deadlines;
- 100-replication baseline/3x-surge matrix with paired bootstrap intervals;
- bounded low-burden observation catalogue.

## Implemented in TL-04 / TL-04.5

- FastAPI product endpoints for live state, scenario changes, deterioration, decisions, audit and evaluation;
- FHIR-like JSON plus manual JSON intake with explicit source provenance;
- SQLite decision/audit persistence with prototype hash-chain integrity;
- one consolidated patient action when rules, uncertainty, deterioration and wait triggers coincide;
- explicit degraded mode: last-verified state is labelled stale, live ETA/Slack is suppressed, digital actions are disabled and the local downtime workflow remains authoritative;
- site/load alert workload measured per configured reassessment-nurse hour.
