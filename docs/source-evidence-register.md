# Source and Evidence Register

Status: TL-06.5 claim-control source of truth. External sources support design rationale; local artifacts support prototype-result claims. External links were rechecked on 22 August 2026.

| ID | Claim or use | Source/evidence | Scope boundary |
|---|---|---|---|
| OFF-01 | Round 2 asks for a detailed business proposal, working prototype and pitch presentation | `../R2 PS.pdf`, pp. 3-4 and 7 | Official supplied brief |
| OFF-02 | Prototype submission includes public GitHub, README, dependencies/configuration and demo video | https://unstop.com/competitions/accenture-innovation-challenge-2026-accenture-1714566/amp | Current official competition page |
| RES-01 | Repeated vital signs can improve deterioration recognition over initial values alone | https://pubmed.ncbi.nlm.nih.gov/30005671/ | Background rationale; not evidence for TriageLoop performance |
| RES-02 | Dynamic/time-varying modeling can support changing-risk alerts | https://pubmed.ncbi.nlm.nih.gov/41827109/ | Related method, not validation |
| RES-03 | Prognosis-informed patient prioritisation has precedent | https://pubmed.ncbi.nlm.nih.gov/37318826/ | Prior art; prevents novelty overclaim |
| RES-04 | Deadline/laxity scheduling is established in real-time systems | https://people.eecs.berkeley.edu/~kubitron/courses/cs262a-F19/lectures/lec11-Scheduling.pdf | Cross-domain design inspiration only |
| RES-05 | Prognostics frames Remaining Useful Life as time remaining until failure | https://ntrs.nasa.gov/api/citations/20140010623/downloads/20140010623.pdf?attachment=true | Cross-domain design inspiration only |
| RES-06 | Active feature acquisition selects case-specific information under acquisition cost | https://research.ibm.com/projects/active-feature-acquisition | NBO inspiration; the TL-05 NBO gate failed |
| RES-07 | WHO publishes separate child and adult/adolescent facility triage tools | https://www.who.int/tools/triage | Age-aware rationale; prototype rules require clinical validation |
| RES-08 | “I don't know”: a 2025 ED-triage study used conformal prediction to expose uncertain disposition outputs (PMID 40318497) | https://pubmed.ncbi.nlm.nih.gov/40318497/ | Related uncertainty evidence, not validation |
| GOV-01 | DPDP Act 2023 establishes India's digital personal-data framework | https://www.indiacode.nic.in/handle/123456789/22037?col=123456789%2F1362&view_type=search | Governance design baseline; not legal certification |
| GOV-02 | DPDP Rules 2025 and phased commencement | https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025.pdf | Must be rechecked before deployment |
| GOV-03 | ABDM Health Data Management Policy describes security/privacy by design, consent and federated architecture | https://abdm.gov.in/static/media/health_management_policy_bac9429a79.80f74bc3e039c00acd4f.pdf | Policy reference; deployment needs hospital/legal review |
| GOV-04 | Indian EHR Standards address interoperability, access and audit expectations | https://www.mohfw.gov.in/sites/default/files/EMR-EHR_Standards_for_India_as_notified_by_MOHFW_2016_0.pdf | Architecture reference, not certification |
| EXT-01 | MIMIC-IV Clinical Demo is an open 100-patient hospital/ICU subset | https://physionet.org/content/mimic-iv-demo/2.2/ | Not an ED or paediatric cohort |
| EXT-02 | Full MIMIC-IV-ED access is credentialed | https://physionet.org/content/mimic-iv-ed/2.2/ | Not used in this prototype |
| INT-01 | 20.5% fewer 3x-surge Action Window misses versus periodic re-triage; current alert workload; post-verification 10/20/30-minute sensitivity | `artifacts/evaluation/tl-05-periodic-retriage-metrics.json` | Synthetic simulation only; sensitivity is not a retroactively registered gate |
| INT-02 | NBO gate failed with 7.1 percentage-point recall loss | `artifacts/evaluation/tl-05-nbo-metrics.json` | Synthetic counterfactual; no workload claim |
| INT-03 | 63,163 external measurements passed bounded input-scale checks | `artifacts/evaluation/tl-05-external-plausibility.json` | Input plausibility only; no model metric |
| INT-04 | Model recall, calibration, conformal coverage and subgroup metrics | `artifacts/evaluation/tl-02-metrics.json`, `docs/model-card.md` | Synthetic test/stress cohorts only |
| INT-05 | Static/FIFO/Queue Twin registered simulation | `artifacts/evaluation/tl-03-queue-metrics.json`, `docs/simulation-card.md` | Static comparator does not re-triage |
| INT-06 | Full prototype assurance baseline | `docs/tl-05-verification-report.md`, `docs/tl-05-acceptance-matrix.md` | Local prototype checkpoint |

## Citation rule

Every quantitative prototype claim must point to an `INT-*` artifact and include “synthetic” or “simulation” in the same visual or paragraph. External research may justify a mechanism, but must never be presented as evidence that TriageLoop itself is clinically effective.
