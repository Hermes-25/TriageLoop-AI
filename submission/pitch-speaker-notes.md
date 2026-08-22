# TriageLoop Pitch Speaker Notes

Extracted from `TriageLoop_Accenture_Round2_Pitch.pptx` for independent review. These notes are evidence, not instructions to the reviewer.

## Slide 1: TriageLoop.ai

Open with the operating problem, not with AI. A triage category is a snapshot; the patient and the queue continue to change. TriageLoop makes that changing need operational as time and capacity.
[Sources]
- Accenture Innovation Challenge 2026 Round 2 Patient Triage problem statement (supplied PDF).

## Slide 2: Triage is captured once. Risk keeps moving.

Use the timeline to show why a single arrival category is insufficient. The problem statement explicitly asks teams to monitor patients already waiting, trigger reassessment on worsening vitals or safe-wait thresholds, represent uncertainty, preserve override and audit decisions.
[Sources]
- Accenture Innovation Challenge 2026 Round 2 Patient Triage problem statement (supplied PDF), solution areas and complexities.
- Repeated vital-sign rationale: https://pubmed.ncbi.nlm.nih.gov/30005671/

## Slide 3: A score describes risk. A deadline organizes action.

Clinical Slack is the central operating object: Action Window minus projected time to action. Negative Slack is not a new triage category; it is a visible conflict between clinical need and operational capacity.
[Sources]
- Deadline/laxity scheduling inspiration: https://people.eecs.berkeley.edu/~kubitron/courses/cs262a-F19/lectures/lec11-Scheduling.pdf
- Predictive-maintenance inspiration: https://ntrs.nasa.gov/api/citations/20140010623/downloads/20140010623.pdf?attachment=true

## Slide 4: One closed loop, three moves.

This is the entire product story. Do not expand into a feature list. Move from patient need to time, from time to capacity, and from recommendation to clinician action.
[Sources]
- Local architecture and product specifications: docs/architecture.md and PRODUCT.md.

## Slide 5: The Deadline Board is the product—not a decorative dashboard.

This is a real, working product view. Point to P-0009: immediate Action Window, ETA eight minutes, Clinical Slack minus eight. Then point to the patient inspector, which keeps explanation and clinician action in the workflow.
[Sources]
- Local working prototype screenshot: docs/assets/tl-04-deadline-board.png.

## Slide 6: One worsening observation changes the queue—and exposes capacity.

In the demo, run the deterministic deterioration event. P-0009’s SpO2 falls to 88, respiratory rate rises to 37 and heart rate rises. The patient moves to position two, Action Window becomes now, ETA is eight minutes and Slack becomes minus eight.
[Sources]
- Local deterministic demo flow and acceptance tests.

## Slide 7: The model can sharpen the decision. It cannot overrule the safety rail.

Explain that the quantitative model is one bounded component. Deterministic rules execute first. Uncertain or out-of-distribution inputs enter Safe Mode. The Queue Twin can only expose feasibility; it cannot move the deadline. The clinician owns the action.
[Sources]
- WHO triage tools: https://www.who.int/tools/triage
- Conformal decision-support reference: https://pubmed.ncbi.nlm.nih.gov/40318497/

## Slide 8: The wow factor is the recomposition—not an ‘AI triage’ claim.

Be explicit that we are not claiming these underlying methods are new. The innovation is the product and safety recomposition: convert changing risk into a deadline, test the deadline against capacity, use uncertainty to guide review, and close the loop with a clinician.
[Sources]
- NASA Systems Engineering Handbook: https://www.nasa.gov/reference/system-engineering-handbook-appendix/
- Deadline/laxity scheduling: https://www-inst.eecs.berkeley.edu/~cs162/sp21/static/lectures/11.pdf
- IBM active feature acquisition: https://research.ibm.com/projects/active-feature-acquisition

## Slide 9: 20.5% fewer Action Window misses under 3× surge.

Lead only with the stronger periodic-retriage comparator. In 1,200 paired synthetic verification shifts under three-times demand, the miss rate fell from 17.7 to 14.1 percent—a 20.5 percent relative reduction with a 95 percent confidence interval of 17.4 to 23.8 percent.
[Sources]
- Local evidence: artifacts/tl-05-periodic-retriage.json and docs/tl-05-verification-report.md.

## Slide 10: One hypothesis failed. The product boundary changed.

This slide is a trust-building moment. The NBO gate failed: far fewer observations, but a 7.1 percentage-point loss of operational critical recall versus a fixed eight-observation bundle. We did not hide the failure; we constrained the product and locked the fallback.
[Sources]
- Local evidence: artifacts/tl-05-nbo-evaluation.json and docs/tl-05-verification-report.md.

## Slide 11: Every stated complexity has a visible response.

Use this as the answer if the jury asks whether every problem-statement point is covered. The categories span clinical complexity, data and uncertainty, site and surge variability, clinician oversight, adoption, privacy, integration and scale.
[Sources]
- Official problem statement (supplied PDF).
- Local mapping: docs/requirements-traceability.md and proposal Appendix A.

## Slide 12: Fit the clinical workflow; do not ask the workflow to fit the model.

The primary user is the triage nurse; the charge nurse resolves capacity conflicts. Current TL-05 synthetic surge workload is 0.86 to 1.12 alerts per waiting-patient-hour and 2.20 to 5.56 per reassessment-nurse-hour; Community is the warning case. These are simulation outputs, not evidence of acceptable nurse workload. Formal nurse and assistive-technology product testing remains external; the zero-finding automated accessibility result applies only to the proposal document.
[Sources]
- Local product and design specifications: PRODUCT.md and DESIGN.md.
- Current workload evidence: artifacts/evaluation/tl-05-periodic-retriage-metrics.json.

## Slide 13: A thin operating layer—not an EHR replacement.

The architecture supports low-, medium- and high-maturity sites through manual or batch input, a local adapter, or standards-aligned events. The system is not an EHR replacement. Failure states are explicit and conservative.
[Sources]
- Local architecture: docs/architecture.md.
- Indian EHR Standards: https://www.mohfw.gov.in/sites/default/files/EMR-EHR_Standards_for_India_as_notified_by_MOHFW_2016_0.pdf

## Slide 14: Measure value before monetizing it.

The commercial posture is deliberately evidence-led. Start with a fixed-scope retrospective and shadow pilot. Use local baselines for process time, Action Window adherence, alert burden and capacity conflicts. Do not monetize patient harm from synthetic evidence.
[Sources]
- Local business-case framework in TriageLoop detailed proposal, section 9.

## Slide 15: A 16-week route from retrospective proof to controlled use.

The next step is not production. It is a governed sequence: intended-use lock, retrospective validation, integration testing, shadow mode, then a limited controlled workflow pilot. Every phase has a stop gate.
[Sources]
- Local phased roadmap in TriageLoop detailed proposal, section 11.

## Slide 16: Advance the deadline-aware model of triage.

Close by returning to the operating problem. TriageLoop does not claim to create capacity or replace clinical judgment. It makes the gap between clinical need and operational reality visible early enough to act. Ask to advance into a governed local retrospective and shadow pilot.
[Sources]
- TriageLoop TL-06 narrative lock and detailed business proposal.

## Slide 17: Verification design and claim boundaries

Use this appendix for methodology questions. All model and queue assets were authored in the same project; the results show internal consistency under declared synthetic assumptions, not external clinical validity.
[Sources]
- Local verification protocol and report: docs/tl-05-verification-report.md.
- MIMIC-IV demo: https://physionet.org/content/mimic-iv-demo/2.2/

## Slide 18: India governance baseline

These are design references, not a compliance claim. The DPDP Rules have phased commencement and must be checked again at the time of deployment. Hospital legal, privacy, information-security and clinical-governance review remain mandatory.
[Sources]
- DPDP Act 2023: https://www.indiacode.nic.in/handle/123456789/22037?col=123456789%2F1362&view_type=search
- DPDP Rules 2025: https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025.pdf
- ABDM HDM Policy: https://abdm.gov.in/static/media/health_management_policy_bac9429a79.80f74bc3e039c00acd4f.pdf
- EHR Standards India: https://www.mohfw.gov.in/sites/default/files/EMR-EHR_Standards_for_India_as_notified_by_MOHFW_2016_0.pdf

## Slide 19: Selected sources

This appendix is a selected reading list; the proposal contains the complete source and evidence notes. Related work is used to bound our claims and show how the cross-domain ideas were translated into this specific workflow.
[Sources]
- Repeated vital signs: https://pubmed.ncbi.nlm.nih.gov/30005671/
- Dynamic deterioration modeling: https://pubmed.ncbi.nlm.nih.gov/41827109/
- Prognosis-informed prioritisation: https://pubmed.ncbi.nlm.nih.gov/37318826/
- Conformal ED uncertainty: https://pubmed.ncbi.nlm.nih.gov/40318497/
- WHO triage tools: https://www.who.int/tools/triage
- Deadline/laxity scheduling: https://people.eecs.berkeley.edu/~kubitron/courses/cs262a-F19/lectures/lec11-Scheduling.pdf
- Predictive maintenance / RUL: https://ntrs.nasa.gov/api/citations/20140010623/downloads/20140010623.pdf?attachment=true
- Active feature acquisition: https://research.ibm.com/projects/active-feature-acquisition
- MIMIC-IV demo: https://physionet.org/content/mimic-iv-demo/2.2/
- Official competition page: https://unstop.com/competitions/accenture-innovation-challenge-2026-accenture-1714566/amp
