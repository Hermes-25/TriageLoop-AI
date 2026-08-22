# Data Boundary

## Planned directories

- `specs/` - generator and scenario specifications.
- `fixtures/` - 24-30 curated human-readable cases.
- `generated/` - ignored reproducible datasets.
- `external/` - optional deidentified external data instructions; data files remain ignored.

## Generation targets

- approximately 10,000 longitudinal encounters;
- paediatric/adult/geriatric strata;
- approximately 50% prior-history availability;
- ambiguous and under-reported presentations;
- baseline, deterioration, recovery and noisy/missing trajectories;
- separate development, calibration, test and shift/stress parameter regimes;
- deterministic seed `20260821` unless versioned configuration changes it.

No identifiable or real patient data belongs in this repository.

## TL-01 realized artifacts

- `specs/generator-config.json` locks seed, size, split and cohort targets.
- `fixtures/curated-cases.json` contains 28 named, human-readable regression/demo cases.
- `generated/encounters.jsonl` contains 10,000 encounters after local generation and is ignored by Git.
- `generated/manifest.json` records realized cohort, split, trajectory and history counts.

Run `python services/api/scripts/generate_data.py` from the repository root to reproduce both the population and curated fixture file.
