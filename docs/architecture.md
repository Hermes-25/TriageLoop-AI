# System Architecture

Status: TL-00 architecture lock.

## 1. Architectural principles

- Hybrid safety system: deterministic rules protect hard boundaries; ML estimates trajectory; simulation estimates capacity feasibility.
- Human-led decisions: recommendations are advisory, explainable, overridable and auditable.
- Modular degradation: each intelligence layer can fail independently without removing the deterministic safety path.
- Versioned contracts: UI, API, model and simulator communicate through plain versioned JSON.
- Reproducible prototype: deterministic seeds, explicit configuration and one-command local startup.
- No LLM in the quantitative clinical path.

## 2. Logical flow

```text
Patient intake / observation
          |
          v
Validation + provenance + freshness
          |
          v
Age-aware deterministic safety gate ---- hard red flag ----> Recommend immediate review
          |
          v
Trajectory feature builder
          |
          v
Discrete-time hazard model + calibration
          |
          v
Conformal prediction set + OOD/data-quality checks
          |
          +---- unreliable ----> Safe Mode + specific reassessment reason
          |
          v
Dynamic Action Window
          |
          v
Queue Twin ETA ------> Clinical Slack / capacity conflict
          |
          v
Next Best Observation (when decision-relevant uncertainty remains)
          |
          v
Nurse: accept / modify / override
          |
          v
Append-only audit event + updated patient state
          |
          +--------------------> loop on time/new observation
```

## 3. Deployment units

### `apps/web` - Next.js App Router

- Default Node.js runtime; no Edge dependency.
- Server Components load the initial board and configuration.
- Client Components handle simulated-clock controls, filters, patient interaction and live updates.
- All server-to-client props are JSON-serializable.
- FastAPI remains the source for patient/decision/simulation state.
- Live update primary path: Server-Sent Events; fallback: bounded polling/manual refresh.
- Production build will use `output: "standalone"` for container portability.

Planned routes:

- `/` - redirect/entry to live board.
- `/board` - nurse waiting-room board.
- `/patients/[patientId]` - patient detail and trajectory.
- `/surge` - charge-nurse capacity view.
- `/evaluation` - policy comparison and evidence.
- `/audit` - filtered prototype audit explorer.
- `/about` - limitations, model/data cards and governance.

### `services/api` - FastAPI

Planned modules:

- `ingestion` - patient/observation validation, provenance and freshness.
- `safety` - age-aware red flags, plausibility and fallback rules.
- `trajectory` - feature construction and time-indexed state.
- `models` - hazard prediction, calibration and model registry.
- `uncertainty` - conformal sets, reliability and OOD.
- `action_window` - conservative window calculation.
- `observation` - Next Best Observation catalogue and policy.
- `queue` - ETA, Clinical Slack and simulation policies.
- `audit` - immutable-style event creation/query.
- `evaluation` - experiment orchestration and metrics.

Planned API surface:

- `GET /v1/health`
- `GET /v1/config`
- `GET /v1/patients`
- `POST /v1/patients`
- `GET /v1/patients/{id}`
- `POST /v1/patients/{id}/observations`
- `GET /v1/patients/{id}/recommendation`
- `POST /v1/patients/{id}/decisions`
- `GET /v1/patients/{id}/audit`
- `GET /v1/events/stream`
- `POST /v1/simulations`
- `GET /v1/simulations/{id}`
- `GET /v1/evaluations/latest`

### Storage and artifacts

- SQLite: patient state, observations, recommendations, clinician decisions and audit events.
- Parquet/CSV: generated synthetic data and evaluation outputs.
- JSON/YAML: site profiles, rule configuration, observation catalogue and policy settings.
- Joblib/JSON: fitted model and calibration artifacts with checksums/version metadata.

## 4. Decision orchestration

The API owns orchestration. The web interface never independently calculates clinical risk, Action Windows or priority.

```text
validated input
  -> safety result
  -> feature state
  -> hazard curve
  -> calibrated/conformal uncertainty
  -> Action Window
  -> queue ETA
  -> Clinical Slack
  -> Next Best Observation if required
  -> recommendation envelope
  -> audit event
```

The recommendation envelope always contains deterministic rule output even when the ML or queue layer is unavailable.

## 5. Audit event model

Each material transition creates a new event rather than overwriting history:

- patient registered;
- observation recorded/corrected;
- rule evaluated;
- prediction generated;
- uncertainty/Safe Mode evaluated;
- Action Window calculated;
- queue ETA/Clinical Slack calculated;
- observation recommendation generated;
- clinician accepted/modified/overrode;
- resource/queue state changed.

Every event includes event ID, timestamp, actor/role, patient pseudonym, correlation ID, input references, component versions, output, explanation codes and previous-event hash. The hash chain is a prototype integrity mechanism, not a claim of production immutability.

## 6. Security and privacy posture

- Synthetic data only.
- No secrets in source control.
- Role-specific prototype views: nurse, charge nurse and evaluator/admin.
- Minimum necessary fields displayed per view.
- Local database excluded from source control.
- Exported evidence uses pseudonymous case IDs.
- Data retention and reset are explicit configuration/actions.

## 7. Failure boundaries

| Failure | Degraded behaviour |
|---|---|
| Model unavailable | Rules + fixed category window + review |
| Calibration artifact unavailable | Conservative threshold + review; label uncertainty unavailable |
| OOD/data-quality failure | Safe Mode |
| Queue simulator unavailable | Clinical requirement shown; feasibility marked unknown |
| Audit persistence failure | Block state-changing clinician action and show error; do not silently proceed |
| Live event stream unavailable | Polling/manual refresh |
| Web unavailable | API and exported scripted evidence remain reproducible |

## 8. Testing layers

- Unit tests: formulas, rules, schemas, conformal logic, window bounds and audit hashing.
- Contract tests: JSON schemas and API response compatibility.
- Scenario tests: every required clinical/brief case.
- Simulation tests: paired policies and seeded reproducibility.
- Browser tests: hero journey, surge, override and audit.
- Safety tests: Safe Mode triggers and no-autonomous-downgrade invariant.

