# TL-04 Product Checkpoint

Date: 22 August 2026  
State: **Amended by TL-04.5 independent-review pass**

Verified product preview: [`assets/tl-04-deadline-board.png`](assets/tl-04-deadline-board.png)

## Product delivered

TriageLoop is now a working nurse-facing clinical deadline workspace rather than a model demonstration. Its primary surface is a dense waiting-room queue paired with a persistent patient inspector. The product exposes the six facts needed for action in a stable order: **what to do, by when, predicted action time, Clinical Slack, what changed and what the clinician decided**.

### Working routes

- `/board` — live Action Window queue, filters, search, deterioration and patient inspector.
- `/surge` — baseline/3× capacity state and Clinical Slack distribution.
- `/evaluation` — predeclared gates, paired simulation outcomes and claim boundaries.
- `/audit` — append-only decision events with actor, reason and tamper-evident hash linkage.
- `/about` — system method, human-authority boundary and India governance framing.
- `/patients/{id}` — direct handoff into the selected patient context.

### Working hero journey

1. Start in baseline: 20 waiting patients and zero capacity conflicts.
2. Apply the deterministic P-0009 deterioration event.
3. Repeat vitals change from the prior observation; the four-horizon trajectory rises.
4. The Action Window contracts, ETA exceeds it and Clinical Slack becomes negative.
5. The queue remains positionally valid, P-0009 is selected and the capacity banner declares one infeasible deadline.
6. A clinician accepts, modifies or overrides the recommendation; modify/override require a documented reason.
7. The exact recommendation-linked decision appears in the audit ledger with actor and hash-chain evidence.

## Product signatures

1. **Deadline before score** — the primary number is an Action Window, joined to operational ETA by Clinical Slack.
2. **Capacity truth** — the interface states when the current queue cannot meet a clinical need; it never implies software creates beds or staff.
3. **Uncertainty creates work** — Safe Mode and Next Best Observation produce a conservative action instead of a decorative confidence badge.
4. **One signal per patient** — rules, model, worsening observations and waiting thresholds resolve into one current action, limiting alert fatigue.
5. **Human accountability** — decisions remain clinician-led and are recorded against the exact recommendation and component versions.

## Verification completed

- 55 Python model, safety, queue, product-store and API tests pass after TL-04.5.
- TypeScript type-check passes.
- Optimized Next.js production build passes for all product routes.
- Browser-verified baseline, deterioration, negative Slack, surge/capacity, override and audit journeys.
- Browser-verified 1,800-shift evaluation evidence route.
- Browser-verified desktop and 390×844 responsive workflows with no horizontal page overflow.
- Visible controls have accessible names; pages have one H1, scoped table headers, high-contrast focus and a keyboard skip link.
- No runtime error overlay was present in the verified journeys.

## Known boundaries retained deliberately

- Synthetic data only; no clinical validation or real-world efficacy claim.
- Demo queue uses 12 curated patients for readable live interaction; the full 28-case fixture and 10,000-encounter generator remain available for verification.
- SQLite hash chaining is tamper-evident prototype evidence, not production immutability.
- Thresholds and deterministic rules require clinical-governance validation before any real use.
- TL-05 must run the complete acceptance matrix, failure injection, security/privacy checks and formal accessibility review.

## TL-04.5 amendment

Before TL-05, the independent critique was checked against the current product rather than accepted at face value. Confirmed gaps were corrected: patient-first framing, synthetic-evidence prominence, exact static-comparator wording, Community residual-risk disclosure, nurse-alert burden, compound-trigger resolution, degraded-mode behavior, manual JSON intake, rounded time presentation, DPDP phase-in language and related-work positioning. Full disposition and verification evidence are in `tl-04.5-critique-disposition.md` and `tl-04.5-checkpoint.md`.

## Executive approval requested

Approve the **Deadline Board + Patient Inspector** as the locked product direction and authorize TL-05 verification. The fallback is not a redesign: if usability testing rejects the split workspace, preserve the same decision object and switch only the presentation to a queue-first drill-down view.
