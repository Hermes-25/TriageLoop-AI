# Problem Statement Traceability

Status: TL-07 repository publication and Docker verification are complete; final portal identity, preferred video-link and submission evidence remain outstanding.

| ID | Brief requirement / complexity | Planned visible evidence | Planned automated evidence | Phase |
|---|---|---|---|---|
| PS-01 | Ambiguous and overlapping symptoms | Named ambiguous fixtures exist; uncertainty/NBO follows in TL-02/04 | `test_required_edge_case_coverage` | TL-01/TL-04 |
| PS-02 | Under-reporting and atypical presentation | Reported-symptom/observed-cue disagreement encoded in curated cases | `test_required_edge_case_coverage` | TL-01/TL-05 |
| PS-03 | Paediatric/adult/geriatric differences | Age-banded cohorts, cases and deterministic reasons implemented | `test_age_bands`, `test_hard_red_flags_escalate_to_level_one` | TL-01 |
| PS-04 | Mixed/limited intake data | Completeness/reliability, missing fields and Safe Mode implemented | `test_bad_or_stale_data_activates_safe_mode` | TL-01/TL-02 |
| PS-05 | Zero-history patient | Contract rejects prior-record leakage; fixture completes without history | `test_zero_history_cannot_leak_prior_records`, `test_required_edge_case_coverage` | TL-01/TL-04 |
| PS-06 | Explainability within seconds | Envelope and working inspector provide action, time, change, local factors, uncertainty and a bounded first-step NBO | Recommendation tests; browser-verified inspector; NBO safety fallback | TL-02/TL-04/TL-05 |
| PS-07 | Asymmetric under-/over-triage harm | 5:1/10:1/20:1 analysis and recall-constrained operating points recorded | `tl-02-metrics.json`, `test_recall_and_calibration_gates` | TL-02/TL-05 |
| PS-08 | Different hospital size/specialty/staffing | Community/regional/urban-trauma profiles and five resource types implemented | `test_full_registered_matrix_ran`, site configuration | TL-03/TL-05 |
| PS-09 | Clinician review and override | Working accept/modify/override panel; modify/override require a reason and show a receipt | Product-store test; browser-verified override journey; `docs/assets/tl-04-deadline-board.png` | TL-04/TL-05 |
| PS-10 | Clear audit trail | Working newest-first ledger exposes actor, reason and recomputed SHA-256 chain status | Tamper-detection test; live override-to-audit journey; `/v1/audit/integrity` | TL-04/TL-05 |
| PS-11 | Integration maturity varies | FHIR-like JSON, CSV and provenance-validated manual JSON input modes | Contract tests; `POST /v1/intake/manual`; API documentation | TL-01/TL-04.5 |
| PS-12 | Data strategy and weighting | Data dictionary, provenance, freshness, missingness/reliability implemented | `test_valid_contract_round_trip`, generator manifest | TL-01 |
| PS-13 | Hybrid model and own uncertainty | Rules, calibrated four-horizon hazard, Mondrian set, OOD and Safe Mode integrated | `test_critical_conformal_coverage_gate`, `test_hard_rule_wins_and_window_is_immediate` | TL-02 |
| PS-14 | Workflow differs during surge | Baseline/3× scenario control recalculates ETA/Slack and visibly declares infeasible capacity | Queue gates; `test_surge_recalculates_slack_and_keeps_capacity_truth_visible`; browser scenario check | TL-03/TL-04 |
| PS-15 | Fail-safe defaults | Missing/stale/implausible/OOD/near-term ambiguity preserve priority and can enter Safe Mode; outage UI suppresses live estimates and routes to downtime protocol | Safety tests; compound-trigger test; browser-visible resilience demonstration on `/about` | TL-01/TL-02/TL-04.5/TL-05 |
| PS-16 | Monitor patients already waiting | Working deterioration event appends a reassessment, updates trajectory/deadline and reorders the live queue | Queue test; product-store deterioration test; browser hero-journey check | TL-01/TL-03/TL-04 |
| PS-17 | Trigger on safe-wait threshold | Fixed category bound creates reassessment due state | `test_wait_threshold_triggers_reassessment` | TL-01 |
| PS-18 | Trigger when rerecorded vitals worsen | Repeat-vital deltas visibly constrain the Action Window and create a capacity conflict when ETA exceeds it | Model/queue tests; browser deterioration check | TL-01/TL-02/TL-04 |
| PS-19 | Adoption and change management | One consolidated patient action, quiet unchanged rows, reasoned overrides, visible synthetic/shadow-mode boundary and quantified per-nurse alert burden | UI research record, working product and `docs/simulation-card.md`; rollout plan remains TL-06 | TL-04/TL-04.5/TL-06 |
| PS-20 | Patient data protection | Pseudonymous synthetic-only UI, strict patient contract, role context, restricted CORS and no-secret repository configuration implemented | Direct-identifier rejection, live CORS/method/input-bound tests; policy/retention package remains TL-06 | TL-04/TL-05/TL-06 |
| PS-21 | Scalability | Configurable site profiles and versioned adapters | `SIM-SCALE-001` | TL-03/TL-05 |
| PE-01 | Score at least 15-20 records | 28 curated cases ready for board/model scoring | `test_exactly_twenty_eight_unique_cases` | TL-01/TL-05 |
| PE-02 | Ambiguous case | Named ambiguous cases present | `test_required_edge_case_coverage` | TL-01/TL-05 |
| PE-03 | Paediatric/geriatric case | Multiple paediatric and geriatric cases present | `test_required_edge_case_coverage` | TL-01/TL-05 |
| PE-04 | Zero-history case | Zero-history case and contract behavior present | `test_zero_history_cannot_leak_prior_records` | TL-01/TL-05 |
| PE-05 | 3x surge | 900 registered surge policy shifts plus 600 stronger-comparator surge shifts and paired bootstrap evidence complete | Registered and periodic-retriage matrix tests | TL-03/TL-05 |
| PE-06 | Explicit confidence with every score | Every recommendation carries horizon risks, conformal set, state, abstention, OOD and quality | recommendation contract; `test_critical_conformal_coverage_gate` | TL-02/TL-05 |
| PE-07 | Clinician override and log | Working override panel and reason-bearing audit entry | Product-store test; browser-verified end-to-end journey | TL-04/TL-05 |
| RP-01 | 100-500+ visits/day | 100/300/550 visits-day profiles executed | `test_full_registered_matrix_ran` | TL-03 |
| RP-02 | Standard or alternative severity framework | FIFO, initial five-level static, fixed 15-minute periodic re-triage and no-demotion dynamic policy compared | TL-03 and TL-05 machine-readable metrics | TL-03/TL-05 |
| RP-03 | Roughly half with prior record | 4,921 some-history / 5,079 no-history in locked 10,000 run | generator manifest; `test_population_includes_all_age_and_history_groups` | TL-01/TL-05 |
| RP-04 | Named jurisdiction | India governance page in proposal/about view | `DOC-GOV-INDIA` | TL-04/TL-06 |
| DEL-01 | Detailed business proposal | 18-page proposal delivered as DOCX and rendered PDF with business case, roadmap, risks/mitigations and a six-screen product appendix | Zero findings in the automated proposal-document accessibility audit; 18-page visual inspection; formal nurse/assistive-technology product usability remains external | TL-06/TL-07 |
| DEL-02 | Working prototype | Live deadline board, patient inspector, baseline/surge, deterioration, decisions, evidence, resilience and audit routes implemented | 73-test suite, production build, live full-story and degraded-mode recovery verified | TL-04/TL-04.5/TL-05/TL-06.5/TL-07 |
| DEL-03 | Pitch presentation | 19-slide editable pitch with working product, safety architecture, evidence, NBO failure, business case and appendices | 19 artifact renders + 19-slide PowerPoint PDF inspected; text claim scan | TL-06/TL-07 |
| DEL-04 | Public repository + README | Source, dependencies, configuration, execution, architecture, evidence and safety boundaries published at `Hermes-25/TriageLoop-AI` | 73 tests, type-check, production build and Docker Compose browser/restart/persistence/reset gates pass; public CI included | TL-06/TL-06.5/TL-07 |
| DEL-05 | Prototype demo video | 2:05 captioned MP4 covers deterioration, NBO boundary, surge, override, audit and evidence; transcript included | 1440×900 H.264 file and representative frames inspected; published as a downloadable `v1.0.0` release asset | TL-07 |

## Traceability release rule

No row may remain without either working visible evidence, an automated/documented verification, or an explicit limitation accepted by Abhishek. “Implemented somewhere in code” is not sufficient for competition coverage.
