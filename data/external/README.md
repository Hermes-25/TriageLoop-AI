# External verification data

TL-05 uses the open **MIMIC-IV Clinical Database Demo v2.2** only for a bounded input-distribution plausibility check.

Source: <https://physionet.org/content/mimic-iv-demo/2.2/>  
DOI: `10.13026/dp1f-ex47`  
License: Open Data Commons Open Database License v1.0.

Required files:

- `icu/chartevents.csv.gz`
- `icu/d_items.csv.gz`

The raw files are ignored from the repository. Download them directly from the official PhysioNet file URLs, then run `services/api/scripts/run_tl05_external_plausibility.py`. The resulting machine-readable metrics contain source hashes.

This open demo is a 100-patient hospital/ICU subset, not an emergency-department cohort. It cannot validate model calibration, paediatric behavior, deterioration prediction, Action Windows, queue outcomes or clinical benefit.
