# Decision Log

Decisions marked **Locked** control implementation unless an explicit change is recorded.

## D-001 - Product operating model

- Date: 21 August 2026
- Status: **Locked**
- Decision: build a nurse-led loop connecting patient trajectory, Dynamic Action Window, Clinical Slack, Next Best Observation, clinician action and audit.
- Rejected: another static AI triage score; autonomous queue reordering without explicit clinical/capacity reasoning.
- Reason: this is the approved concept, covers the full brief and creates the strongest defensible system-level novelty.

## D-002 - Action Window terminology

- Date: 21 August 2026
- Status: **Locked**
- Decision: use a conservative interval phrased as “recommended within,” bounded by hard rules and category limits.
- Rejected: “remaining safe life,” “safe until,” or an exact deterioration deadline.
- Reason: minute precision would imply an unsupported clinical safety guarantee.

## D-003 - Predictive model family

- Date: 21 August 2026
- Status: **Locked**
- Decision: interpretable discrete-time logistic hazard model at 5/15/30/60-minute horizons, with a gradient-boosted challenger.
- Selection rule: the challenger wins only on meaningful safety/calibration/operational improvement, not AUROC alone.
- Fallback: calibrated horizon classifiers, then transparent trajectory/rule logic.

## D-004 - Data strategy

- Date: 21 August 2026
- Status: **Locked**
- Decision: synthetic longitudinal encounters are the primary dataset; curated fixtures guarantee required edge coverage. MIMIC-IV-ED is optional and non-critical-path.
- Reason: no proprietary data is required; synthetic data supports paediatric, geriatric, ambiguity and surge cases without access delays or false clinical claims.

## D-005 - Safety architecture

- Date: 21 August 2026
- Status: **Locked**
- Decision: rules before model; no autonomous downgrade; uncertainty/OOD/missingness trigger review or Safe Mode.
- Rejected: end-to-end black-box prioritisation.

## D-006 - Uncertainty method

- Date: 21 August 2026
- Status: **Locked**
- Decision: class-conditional/Mondrian conformal prediction evaluated by rare critical-class coverage and review workload.
- Fallback: calibrated ensemble intervals, then conservative quality/critical thresholds.

## D-007 - Next Best Observation boundary

- Date: 21 August 2026
- Status: **Locked**
- Decision: value-of-information ranking over a bounded catalogue of low-burden observations/history questions.
- Rejected: autonomous test ordering or a generic “low confidence” warning without a specific next action.

## D-008 - Queue policy and evaluation

- Date: 21 August 2026
- Status: **Locked**
- Decision: compare FIFO, static five-level triage and TriageLoop on identical seeded shifts across site sizes and baseline/3x surge.
- Primary operational quantity: Clinical Slack = latest recommended action time minus predicted time to that action.

## D-009 - Product architecture

- Date: 21 August 2026
- Status: **Locked**
- Decision: Next.js App Router frontend, Python FastAPI backend, SQLite prototype store and versioned JSON/FHIR-like contracts.
- Live update: SSE with polling/manual-refresh fallback.
- Packaging: local one-command workflow and Docker-compatible standalone Next.js build.

## D-010 - Quantitative role of LLMs

- Date: 21 August 2026
- Status: **Locked**
- Decision: no LLM in the score, hazard, uncertainty, Action Window, queue or priority calculation.
- Optional later use: constrained text structuring or explanation only, with deterministic output checks.

## D-011 - Regulatory framing

- Date: 21 August 2026
- Status: **Locked**
- Decision: assume India; frame privacy/governance against DPDP, ABDM Health Data Management Policy and Indian EHR standards.
- Prototype remains synthetic and is not presented as legally certified.

## D-012 - Evidence and claims

- Date: 21 August 2026
- Status: **Locked**
- Decision: predeclare evaluation gates; report all relevant results and label synthetic/simulation evidence explicitly.
- Prohibited claims: clinical validation, achieved hospital savings/outcomes, production readiness, regulatory approval, patent novelty and “world first.”

## D-013 - Synthetic population split

- Date: 21 August 2026
- Status: **Locked**
- Decision: generate 10,000 encounters from seed `20260821`; hold 500 as an explicit stress cohort and split the remaining 9,500 into 60% training, 20% validation and 20% test.
- Reason: a separate deliberately difficult cohort prevents distribution-shift testing from being diluted into routine holdout performance.

## D-014 - Deterministic-rule status

- Date: 21 August 2026
- Status: **Locked for prototype; requires clinical validation for any real use**
- Decision: implement conservative age-aware extremes, hard observed cues, worsening deltas, category wait bounds and data-quality Safe Mode before ML.
- Reason: the prototype must demonstrate fail-safe precedence and age-aware behavior now, while avoiding the false claim that its thresholds constitute a deployable clinical protocol.

## D-015 - TL-02 model selection

- Date: 22 August 2026
- Status: **Selected, pending executive phase approval**
- Decision: select the calibrated gradient-boosted discrete-time hazard challenger; retain logistic hazard as the interpretable benchmark and fallback.
- Evidence: after removing observation count as a workflow-proxy feature, logistic failed registered short-horizon test/stress recall and stress conformal-coverage gates. The boosted model passed every registered recall, test-calibration and critical-class coverage gate at all four horizons.
- Trade-off: boosting has slightly worse mean test Brier score than logistic (0.0498 versus 0.0476), but materially higher stress recall (0.941 versus 0.862) and gate compliance. Small decision stumps and local contribution summaries preserve a bounded explanation path.

## D-016 - Uncertainty operating point

- Date: 22 August 2026
- Status: **Locked for prototype**
- Decision: use 90% nominal class-conditional/Mondrian conformal sets, calibrated on a validation subset isolated from probability calibration. Retain 95% and 85% sweeps as workload sensitivity evidence.
- Reason: the 90% setting satisfies critical-class coverage gates while avoiding the larger ambiguity/review burden at 95%. Ambiguity drives a targeted observation; only near-term material ambiguity invokes Safe Mode.

## D-017 - Queue policy

- Date: 22 August 2026
- Status: **Locked for prototype, pending executive checkpoint approval**
- Decision: use a no-demotion dynamic category followed by absolute Action Window, calibrated repeat-observation risk, uncertainty and arrival time. Repeat-observation 30-minute risk at/above 0.20 may promote to dynamic level 2; hard rules remain first.
- Reason: pure earliest-deadline scheduling grouped excessive false-positive 30-minute windows and failed the registered gate. The final policy preserves clinician category information, promotes only strong longitudinal evidence, and uses absolute deadlines for waiting-time aging.

## D-018 - Queue evaluation deadline semantics

- Date: 22 August 2026
- Status: **Locked simulation assumption; not a clinical SLA**
- Decision: evaluate the synthetic composite using a 30-minute response allowance after the registered deterioration signal, while hard red flags retain a five-minute bound.
- Reason: the generator target combines broader urgent review/monitoring/treatment escalation with immediate red flags. Sensitivity at 10/20/30 minutes is published because the queue gate depends on this definition.

## D-019 - Capacity claim boundary

- Date: 22 August 2026
- Status: **Locked**
- Decision: claim improved simulated prioritisation and earlier visibility of infeasible deadlines, not that TriageLoop solves ED crowding or determines staffing.
- Evidence: the community 3× profile remains at 0.743 critical recall despite a 20.8% relative miss reduction; its negative Slack must remain visible in the product.

## D-020 - Primary product surface

- Date: 22 August 2026
- Status: **Selected, pending executive phase approval**
- Decision: use a dense Deadline Board plus persistent Patient Inspector, retaining the established ED tracking-board mental model while changing its optimization target to Action Window and Clinical Slack.
- Rejected: generic KPI-card dashboard, tile-first command centre and patient-only timeline as the home surface.

## D-021 - Product alert hierarchy

- Date: 22 August 2026
- Status: **Locked for prototype**
- Decision: consolidate rules, risk, uncertainty, deterioration and wait bounds into one current patient action. Reserve clinical red for hard urgency/capacity conflict; keep brand berry visually distinct; always pair state color with text or icon.
- Reason: the product must reduce alert competition while keeping use-critical changes conspicuous.

## D-022 - Mobile workflow

- Date: 22 August 2026
- Status: **Locked for prototype**
- Decision: desktop shows queue and inspector simultaneously; tablet/mobile use an explicit queue-first drill-down with a persistent return control.
- Reason: a compressed split view damages both situation awareness and patient comprehension on narrow screens.

## D-023 - Demo product state

- Date: 22 August 2026
- Status: **Selected, pending executive phase approval**
- Decision: use 12 curated patients for the deterministic interactive board, with the complete 28-case fixture and 10,000-encounter population retained for automated evidence.
- Reason: 20 patients make the stated prototype minimum directly visible; the scrollable board preserves readability without narrowing the 28-case fixture library.

## D-024 - Independent-review disposition

- Date: 22 August 2026
- Status: **Locked for TL-04.5**
- Decision: treat the independent review as a red-team input, verify each finding against the current repository and publish a finding-by-finding disposition. Product-readiness findings based on the earlier pre-TL-04 package are superseded by the working product; evidence, workload, comparator and failure-state findings remain actionable.
- Reason: adopting scores from an outdated evidence pack would be misleading, while dismissing the still-valid scientific criticisms would weaken TL-05.

## D-025 - Comparator claim boundary

- Date: 22 August 2026
- Status: **Locked**
- Decision: define the existing static comparator as initial five-level category plus FIFO within category, with no later observation processing. Add a fixed 15-minute periodic re-triage comparator in TL-05 and lead claims with the stronger comparison once available.
- Reason: the current 36.0% synthetic improvement combines the benefit of reassessment with the benefit of learned dynamic prioritisation; P1b is needed to isolate incremental value more fairly.

## D-026 - Alert-workload disclosure

- Date: 22 August 2026
- Status: **Locked**
- Decision: count consolidated patient-level signals only within the eight-hour shift and report them per configured reassessment-nurse hour for every site/load cell. Do not describe the burden as manageable until tested with nurses.
- Evidence: Community 3x surge produces 5.56 signals per reassessment-nurse hour under the one-nurse assumption and is explicitly retained as a workload warning.

## D-027 - Degraded-mode authority

- Date: 22 August 2026
- Status: **Locked for prototype**
- Decision: during decision-service outage, label retained state as last verified, suppress live ETA/Slack, disable digital decisions and new model processing, retain fixed category bounds and direct users to the local downtime/escalation process. Reconcile decisions after restoration.
- Reason: stale estimates must never masquerade as current clinical state.

## D-028 - Related-work boundary

- Date: 22 August 2026
- Status: **Locked for claims**
- Decision: cite arXiv:2604.00215 as related Indian OPD urgency-drift/queue-optimisation work. Claim differentiation only at the mechanism and product-safety level: conservative Action Windows, Clinical Slack, uncertainty-to-observation workflow, no-demotion rules, compound-trigger resolution and clinician-linked audit.
- Prohibited: claiming the broad idea of dynamic AI queue optimisation as novel or a world first.

## D-029 - External evidence path

- Date: 22 August 2026
- Status: **Locked for TL-05**
- Decision: perform a feasibility-first external plausibility check. Full MIMIC-IV-ED requires a credentialed user, CITI training and a signed DUA, so it is not a silent dependency. Use accessible reference distributions or the public MIMIC-IV demo for bounded input-plausibility checks if credentialed ED data is unavailable; do not present either as prospective clinical validation.

## D-030 - Stronger comparator result

- Date: 22 August 2026
- Status: **Verified and locked for claims**
- Decision: lead the operational evidence with TriageLoop versus fixed 15-minute periodic re-triage, not only versus initial static triage.
- Evidence: 1,200 paired policy shifts show a 20.5% relative reduction in 3×-surge Action Window misses (95% CI 17.4%–23.8%). This is synthetic simulation evidence, not clinical benefit.

## D-031 - NBO release decision

- Date: 22 August 2026
- Status: **Failed gate; safe fallback locked**
- Decision: retain NBO only as a first-measurement suggestion. It may not replace full reassessment or support an efficiency/safety claim.
- Evidence: one observation reduced measurement count by 87.5% but reduced operational critical recall by 7.1 percentage points, beyond the predeclared 2-point limit. The four-observation test-selected fallback failed independent stress confirmation; no post-hoc promotion is allowed.

## D-032 - External plausibility boundary

- Date: 22 August 2026
- Status: **Verified with limitation**
- Decision: use the open MIMIC-IV Clinical Demo only to rule out gross vital-sign input-scale mismatch.
- Evidence: 63,163 mapped measurements across five core vital fields met the declared coverage/range/median checks. The source is a small adult hospital/ICU demo, not an ED cohort; no model metric or clinical-validation claim is permitted.

## D-033 - TL-05 product assurance

- Date: 22 August 2026
- Status: **Verified for prototype checkpoint**
- Decision: expose audit integrity only after recomputing every event hash and link; preserve a safe degraded mode; restrict the local API surface and reject direct identifiers outside the strict synthetic contract.
- Evidence: tamper test detects payload modification; live full-story and outage/recovery journeys pass; CORS, unsupported method and request-length checks pass; production build and the complete automated suite pass.
