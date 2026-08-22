# TL-05 Verification Report

Date: 22 August 2026  
Scope: scientific validity within the declared synthetic system, product behavior, safety, security/privacy boundary, accessibility structure and reproducibility.

## Executive result

TriageLoop passes the TL-05 prototype checkpoint with one important negative finding carried forward as a product constraint. The core deadline-and-capacity loop remains supported: versus fixed 15-minute periodic re-triage, it reduces 3×-surge Action Window misses by 20.5% (95% CI 17.4%–23.8%). The NBO hypothesis fails its recall-preservation gate and is not released as a reassessment replacement or efficiency claim.

## Scientific findings

### Periodic re-triage comparator

The verifier ran two policies across three site profiles, baseline/3× load and 100 paired replications: 1,200 policy shifts. Periodic re-triage processes accumulated observations only at fixed global 15-minute sweeps, uses deterministic rules/category, never demotes, and has no learned risk or uncertainty.

Under 3× surge, TriageLoop versus periodic re-triage produced:

- Action Window miss rate: 17.7% to 14.1%; 20.5% relative reduction (17.4%–23.8%).
- Negative-slack minutes: 14.0% reduction (8.8%–19.7%).
- Signal-to-action time: 15.7% reduction (12.5%–18.9%).
- Low-acuity P90 wait: 14.4% reduction (8.7%–19.5%).

This comparison is the preferred operational headline. It remains a synthetic simulation result. A TL-06.5 post-verification sensitivity analysis against the same periodic comparator found 12.8%/13.0%/24.1% reductions at 10/20/30-minute response definitions (95% CIs 8.9%–16.7% / 6.7%–19.7% / 16.5%–31.3%). All directions stayed positive, but only 30 minutes exceeded 20%; this is not a retroactively registered gate.

The current TL-05 artifact also contains TriageLoop alert workload in every site/load cell. Under surge, the range is 0.86–1.12 consolidated alerts per waiting-patient-hour and 2.20–5.56 per reassessment-nurse-hour. Community surge is the explicit warning case; no safe-workload or manageability threshold is claimed.

### Next Best Observation

On 4,317 eligible test/stress snapshots, one NBO reduced requested measurements from eight to one and estimated catalogue acquisition time by 91.1%, but operational critical recall fell from 0.959 to 0.888: a 7.1 percentage-point loss. The fixed safety boundary was at most 2 points. The gate therefore fails.

The smallest test-selected adaptive fallback used four observations. It passed the test split but failed independent stress confirmation, so it is not qualified. Selecting five after seeing stress would be post-hoc tuning and is not allowed. Safe release behavior is full reassessment or escalation whenever uncertainty or concern remains; NBO is only the first suggested measurement.

### External plausibility

The open MIMIC-IV Clinical Database Demo v2.2 supplied 63,163 deidentified hospital/ICU measurements mapped to heart rate, respiratory rate, SpO2, systolic/diastolic blood pressure and temperature. All five core vital fields were present, at least 95% of each field lay inside prototype hard plausibility ranges, and every external median lay inside the synthetic p01-p99 interval.

This rules out a gross input-unit/scale mismatch only. It does not test ED transfer, labels, calibration, Action Windows, queue outcomes, paediatrics or clinical benefit.

## Product and safety verification

The live full-story path passed: reset -> 3× surge -> P-0009 deterioration -> queue promotion to position 2 with -8 minutes Slack -> reasoned nurse override -> five-event audit chain. P-0008 remained position 1, demonstrating deterministic handling of multiple critical patients. Audit status is derived by recomputing every SHA-256 event hash and previous-link value; direct database tampering is detected by test.

When the API was deliberately stopped, the UI changed to “Decision service degraded,” removed patient data/live estimates, disabled reset, displayed downtime guidance and offered an explicit retry. After restart, retry restored the live board without a false success state.

## Engineering, security and accessibility

- 71 Python tests pass; TypeScript type-check and optimized Next.js production build pass.
- The API rejects an undeclared direct patient-name field, a 501-character override reason and unsupported DELETE reset; malicious origins receive no CORS allow-origin response.
- Frontend responses include nosniff, DENY framing, no-referrer and disabled camera/microphone/geolocation headers.
- Secrets are ignored and no credential material was found in the project scan; generated external/raw data and SQLite state are ignored.
- All five primary routes expose exactly one H1, a skip link and named interactive controls; clinical tables expose headers/captions. Focus-visible and reduced-motion styles are present. Formal nurse/assistive-technology usability remains external validation work.

## Reproducibility

The periodic comparator, NBO evaluation and external plausibility scripts were rerun. Every metrics/case artifact retained the same SHA-256 as its immediately preceding run. Seeded simulation uses base seed 20260822; the selected model remains the separately locked seed-20260821 artifact.

- Periodic metrics: `6b4bed629305c5e447c46ebfeede5725870e88b614ebb0d882f6f3ac8fdd875e`
- Periodic shift rows: `7e9f413b5215e1c0b173ef2f40467a6d4fec0baa1dc7690d00dba14514b9aef9`
- NBO metrics: `2c5fc3840a988c5bffce1a79f100bbf6118dd19cc65771229abc34330da7b36d`
- NBO case rows: `c7fdcd67ae733a5c1d937af10924951b563b52893a3d77e54213ab82ec25a8c1`
- External plausibility: `9e92598d67fd9f2f4254b3ac468a2399e56c6cacfcd0ea90d26ab7836ce718c7`

Machine-readable evidence is in `artifacts/evaluation/tl-05-*.json*`; exact claim disposition is in `docs/tl-05-acceptance-matrix.md`.
