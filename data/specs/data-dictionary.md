# TL-01 Data Dictionary

All records are synthetic and use pseudonymous identifiers. The product-facing `patient` object is separated from hidden synthetic `truth` labels to prevent label leakage.

| Group | Fields | Purpose |
|---|---|---|
| Identity/time | patient ID, encounter ID, arrival and observation times | Longitudinal ordering and waiting-time events |
| Demographics | age, sex at birth, pregnancy status | Age-aware rules and subgroup evaluation |
| Presentation | chief complaint, reported symptoms, observed cues | Preserve ambiguity and report/observation disagreement |
| Prior context | history status, conditions, medications, allergies, frailty | Explicit zero/partial/full-history pathways |
| Repeated observations | heart rate, respiratory rate, SpO2, BP, temperature, GCS, pain, mental status | Trajectory and rule inputs |
| Quality | completeness, reliability, flags, source | Missingness, device warning and Safe Mode evidence |
| Clinician state | assigned level, workflow status, assigning role | No-downgrade baseline and human ownership |
| Provenance | source, generator version, scenario ID | Reproduction and audit |
| Hidden truth | trajectory, critical-within horizons, minimum level, split | TL-02 training/evaluation only; never shown as an observed fact |

## Temporal leakage boundary

At horizon `t`, only observations timestamped at or before `t` may become features. Synthetic event time and `truth` fields are labels, not inputs. Patient-level splits are assigned before TL-02 feature extraction.

## Quality semantics

- Completeness describes populated observation fields.
- Reliability records source/device confidence and is reduced by detected missingness or implausibility.
- Staleness is calculated at evaluation time, not stored as a permanent patient fact.
- Missing, stale or implausible critical data triggers Safe Mode and reassessment; it never licenses lower priority.
