# TL-05 Acceptance Matrix

Date: 22 August 2026  
Decision rule: a failed safety or claim gate is disclosed and routed to its locked fallback; it is never converted into a pass through post-hoc tuning.

| Area | Acceptance check | Evidence | Result |
|---|---|---|---|
| Strong comparator | TriageLoop directionally reduces 3×-surge misses versus fixed 15-minute periodic re-triage; all cells have 100 replications; low-acuity P90 is not >20% worse | 1,200 policy shifts; 20.5% reduction, CI 17.4%–23.8%; low-acuity P90 improves 14.4% | **Pass** |
| NBO | At least 25% fewer observations with no more than 2 percentage points loss of operational critical recall | 4,317 eligible snapshots; 87.5% fewer, but 7.1-point recall loss | **Fail — fallback active** |
| NBO fallback | Test-selected adaptive bundle must independently pass stress confirmation | Four observations pass test but fail stress; no post-hoc selection on stress | **Not qualified** |
| External plausibility | Five core vital fields present; each ≥95% inside hard ranges; external medians inside synthetic p01-p99 | 63,163 MIMIC-IV demo measurements; all declared checks pass | **Pass with scope limitation** |
| Rules and uncertainty | Hard rules precede model; no autonomous downgrade; missing/stale/OOD/ambiguous states fail safely | Registered safety/model/scenario tests | **Pass** |
| Multi-critical queue | Multiple critical patients remain deterministically ranked; capacity conflicts stay visible | P-0008 then deteriorated P-0009 at positions 1/2 under 3× surge | **Pass** |
| Human control and audit | Reasoned override persists; every hash/link is recomputed; direct tampering is detected | Live P-0009 journey, `/v1/audit/integrity`, tamper test | **Pass** |
| Outage behavior | Suppress live clinical state/actions, show downtime guidance, recover explicitly | Browser stop/reload/retry journey | **Pass** |
| API/security boundary | Strict synthetic contract, CORS allowlist, unsupported mutation rejected, bounded reason input, security headers | Direct-identifier 422; malicious origin receives no ACAO; DELETE 405; 501-char reason 422; headers verified | **Pass for local prototype** |
| Accessibility | One H1 per route, skip link, named controls, table headers/captions, focus styling and reduced-motion rule | Browser DOM audit across five routes plus stylesheet review | **Pass for prototype; formal assistive-tech study remains** |
| Reproducibility | Full tests/build pass; TL-05 evaluation artifacts reproduce byte-for-byte | 71 tests, TypeScript, Next production build, repeated SHA-256 comparison | **Pass** |
| Claims | No clinical validation, staffing, savings, production-readiness or novelty-overreach claim | Product copy, model/simulation cards and decision log | **Pass** |

## Residual release limitations

- The evidence is predominantly synthetic and the external source is not an ED cohort.
- Community surge remains capacity constrained; software cannot create staff or space.
- NBO has not earned a workload-reduction claim.
- Clinical usability, accessibility with real assistive technology, local calibration, governance and prospective outcomes remain future hospital-validation work.
