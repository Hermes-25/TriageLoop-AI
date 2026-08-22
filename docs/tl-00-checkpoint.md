# TL-00 Scope and Scientific Contract Checkpoint

Recorded: 21 August 2026, 21:41 IST  
Status: ready for executive approval

## Locked during TL-00

- One product definition and anti-drift priority order.
- Intended use, age bands, setting, jurisdiction and clinical limitations.
- Hybrid safety architecture and Safe Mode invariants.
- Prediction target and four survival horizons.
- Dynamic Action Window definition and prohibited “safe until” framing.
- Under-/over-triage cost sensitivity and conformal uncertainty approach.
- Next Best Observation boundary.
- FIFO/static/TriageLoop paired evaluation design.
- Predeclared synthetic/simulation acceptance gates.
- Next.js/FastAPI/SQLite architecture with versioned contracts and degradation paths.
- Decision log, risk register and problem-statement traceability.

## Executive decisions requested

No unresolved decision currently changes the approved product. Approval of this checkpoint authorizes TL-01 implementation using the following defaults:

1. India jurisdiction and synthetic-data-only critical path.
2. Paediatric <12, adult 12-64, geriatric 65+.
3. Generic five-level static comparator.
4. Discrete-time logistic hazard primary model with boosted challenger.
5. 5/15/30/60-minute risk horizons.
6. Action Window as a conservative interval bounded by rules/category limits.
7. Mondrian conformal uncertainty and Safe Mode.
8. 10,000 generated encounters and 24-30 curated demo cases.

## TL-01 entry criteria

- This checkpoint is approved.
- No change to the clinical safety contract is pending.
- The next command is `START TL-01 DATA`.

## TL-01 exit criteria preview

- Versioned schema validation works.
- Reproducible generator produces the planned splits.
- 24-30 curated fixtures cover every required edge case.
- Age-aware rules and data-quality/Safe Mode inputs pass their registered tests.

