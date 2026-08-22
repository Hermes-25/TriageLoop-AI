# TriageLoop Queue Twin Simulation Card

Status: synthetic operational prototype; not a clinical or staffing model.  
Simulation version: registered matrix `1.1.0`; TL-05 comparator extension `1.2.0`

## Purpose

Test whether deadline-aware prioritisation can reduce simulated clinical-action misses under crowding, expose infeasible capacity through negative Clinical Slack, and avoid starving lower-acuity patients.

## Registered matrix

The registered TL-03 matrix contains 1,800 policy shifts: three policies × three sites × two loads × 100 replications. Each cell contains 100 paired eight-hour shifts. FIFO, static triage and TriageLoop replay identical arrivals, patient templates, service times and resources.

| Profile | Visits/day | Triage nurses | Reassessment nurses | Clinicians | Monitored spaces | Treatment spaces |
|---|---:|---:|---:|---:|---:|---:|
| Community | 100 | 2 | 1 | 2 | 4 | 8 |
| Regional | 300 | 5 | 3 | 6 | 12 | 24 |
| Urban/trauma | 550 | 8 | 5 | 11 | 20 | 40 |

Load states are baseline and 3× arrival surge with fixed staffing. Service durations are 2–5 minutes for triage, 5–9 for reassessment and 10–18 for the next clinician action. Space occupancy is separately simulated. These values are transparent assumptions, not recommendations.

## Policies

- **FIFO:** arrival order, except initially visible hard red flags.
- **Static:** the initial clinician-assigned generic five-level category, then arrival order within category. This comparator does **not** process later observations, elapsed-wait triggers or periodic re-triage; the comparison therefore measures the complete dynamic loop against an initial-category workflow, not against every possible re-triage practice.
- **TriageLoop:** rules first; Living Acuity may promote but never demote the category; equal dynamic levels are ordered by absolute Action Window, calibrated trajectory risk, uncertainty and arrival. New observations can shorten the deadline or create a hard rule. Absolute deadlines provide waiting-time aging.

## Clinical Slack

For each waiting task:

`Clinical Slack = absolute action deadline - projected action start`

Negative Slack is a capacity conflict. The simulator does not relax the clinical deadline when capacity is insufficient.

## Outcome definitions

- **Action Window miss:** next clinical action begins after the synthetic required-action deadline.
- **Critical recall:** one minus critical Action Window miss rate.
- **Negative-slack minutes:** total critical lateness beyond the required-action deadline.
- **Signal-to-action:** minutes from registered deterioration signal to clinical action, floored at zero.
- **Tail guardrail:** P90 wait for static levels 4–5.
- **Waiting-time effectiveness:** mean bounded fraction of each requirement window remaining at action.
- **Rank effectiveness:** ROC rank statistic comparing critical versus non-critical waiting times.

The synthetic deterioration composite receives a configurable 30-minute response allowance after its registered signal. Hard red flags retain a five-minute prototype bound. This distinguishes immediate red flags from broader urgent escalation and is not a clinical SLA.

## Primary results

Across all 3× surge shifts, TriageLoop versus static triage produced:

- 36.0% relative reduction in critical Action Window misses (95% bootstrap interval 31.2%–41.1%) in the registered synthetic 30-minute-response experiment; this result does not hold at the strictest 10-minute definition tested;
- 62.4% reduction in negative-slack minutes (58.7%–66.3%);
- 50.9% reduction in signal-to-action delay (47.4%–54.6%);
- 57.0% reduction in low-acuity P90 wait (52.7%–60.6%).

Baseline cells had zero critical misses under all policies, so no benefit is claimed where capacity was already adequate.

## Consolidated nurse-facing alert workload

An alert is counted only when a patient's deadline materially shortens, a hard rule appears or initial queue projection is already infeasible. Multiple simultaneous signals for that patient are consolidated. The per-nurse quantity divides these events by configured reassessment-nurse hours; it is descriptive and is **not** a validated safe-workload threshold. The figures below are present in the current TL-05 periodic-comparator artifact (`tl-05-periodic-retriage-metrics.json`, TriageLoop cells); they describe the product policy itself and are not attributed to the comparator.

| Site | Load | Reassessment nurses | Mean consolidated alerts / 8h shift | Mean alerts / reassessment-nurse-hour |
|---|---|---:|---:|---:|
| Community | Baseline | 1 | 1.67 | 0.21 |
| Community | 3× surge | 1 | 44.46 | 5.56 |
| Regional | Baseline | 3 | 2.54 | 0.11 |
| Regional | 3× surge | 3 | 63.46 | 2.64 |
| Urban/trauma | Baseline | 5 | 4.41 | 0.11 |
| Urban/trauma | 3× surge | 5 | 88.14 | 2.20 |

Community surge is the clear workload warning: approximately one consolidated signal every 10.8 nurse-minutes under the stated one-reassessment-nurse assumption. Whether that is usable requires nurse task testing; no manageability claim is made.

## Sensitivity and limitations

Against the original initial-category static comparator, surge miss-rate reductions at 10/20/30-minute composite response allowances were 11.1%/28.7%/32.2% in the registered 30-replication sensitivity run.

TL-06.5 added a post-verification sensitivity analysis against the stronger fixed 15-minute periodic-retriage comparator. Across three surge sites and 30 paired replications per site, reductions were **12.8%** (95% CI 8.9%–16.7%) at 10 minutes, **13.0%** (6.7%–19.7%) at 20 minutes and **24.1%** (16.5%–31.3%) at 30 minutes. All directions remained positive, but only the 30-minute definition exceeded 20%. No gate is retroactively imposed; the result remains sensitive to how “action due” is operationalised.

The community 3× case remains capacity constrained: TriageLoop critical recall is 0.743 even after improvement. This is a feature of the evidence—the system exposes scarcity but cannot manufacture staff or space. Results inherit synthetic arrivals, labels, service times and staffing assumptions and require hospital-specific validation.

## TL-05 stronger comparator

The 1,200-policy-shift extension adds **fixed 15-minute periodic re-triage**: two policies × three sites × two loads × 100 replications. Future observations become available only at global 15-minute sweeps, deterministic rules/category can promote but not demote, and the initial category deadline remains absolute from arrival. It does not use learned trajectory risk, conformal uncertainty or continuous event response.

Across the 3× surge cells, TriageLoop reduced Action Window misses by **20.5%** versus this comparator (95% paired-bootstrap interval 17.4%–23.8%), from 17.7% to 14.1%. Negative-slack minutes fell 14.0%, signal-to-action time 15.7%, and low-acuity P90 wait 14.4%. This isolates more incremental value than the original static comparison, but remains synthetic operational evidence.

The v1.1.0 full matrix was rerun twice and produced byte-identical evidence. Metrics SHA-256: `d3be69096e1c6e10b531ea76e2cad85e75428a3f22250cce80f396e5889da73d`; shift-level evidence SHA-256: `34c9053e649eb3589d9082567e765b3e4a83a7b36d4ec75082f635948801e439`.
