# TL-04 UI Research and Product Direction

Status: design direction locked for implementation, 22 August 2026.

## Research synthesis

### 1. Preserve the tracking-board mental model, change what it optimizes

Emergency-department status boards are used to maintain real-time awareness of patient identity/location, assigned staff, pending work and elapsed time. Published ED work also describes the environment as dynamic, multi-patient and coordination-heavy, and reports positive results from work-centered/cognitive-systems-engineering approaches rather than isolated visual redesign ([integrated patient-focused ED display](https://pubmed.ncbi.nlm.nih.gov/31533171/), [EDIS cognitive systems engineering evaluation](https://pubmed.ncbi.nlm.nih.gov/28166896/), [status-board comparison](https://pubmed.ncbi.nlm.nih.gov/20863752/)).

**Applied decision:** TriageLoop keeps a dense, sortable board familiar to ED work, but replaces elapsed-time-only prioritization with Action Window, predicted ETA and Clinical Slack. The innovation is therefore legible inside an established operational form.

### 2. Centralize action, not analytics

GE HealthCare describes command-center products as a unified real-time source for patient flow, capacity, tasks and proactive issue resolution, while Qventus emphasizes surfacing the most impactful actions without making care teams switch interfaces ([GE Command Center](https://www.gehealthcare.com/en-us/products/software/command-center), [Qventus Inpatient Capacity](https://www.qventus.com/solutions/discharge-planning/)). Real ED tracking boards visible in deployed examples are dense tables with acuity, waiting time, location, staff and task state, not marketing-style card grids ([HFM ED tracking-board example](https://www.hfmmagazine.com/articles/3380-improving-patient-flow-in-the-emergency-department), [NHS York electronic whiteboard](https://nhsyork.github.io/2018-12-28-Whiteboards/)).

**Applied decision:** the default view is a queue plus persistent patient inspector. Metrics and evidence receive their own route. No generic KPI-card dashboard sits between a nurse and the next action.

### 3. Make only consequential states loud

AHRQ's patient-safety synthesis recommends reducing low-value alerts, tiering severity and making only severe alerts interruptive; it also cites aviation as a useful high-reliability contrast ([AHRQ PSNet alert fatigue primer](https://psnet.ahrq.gov/primer/alert-fatigue)). The project's own alert contract consolidates multiple model/rule signals into one patient-level action.

**Applied decision:** one consolidated action per patient, silent row updates for unchanged low-priority states, a single system-level capacity banner, and interruptive treatment reserved for hard red flags or persistence failure.

### 4. Treat the interface as a risk control

FDA human-factors guidance frames the interface around what users must perceive, interpret and manipulate, and places use-error reduction ahead of training or labeling alone ([FDA Human Factors and Medical Devices](https://www.fda.gov/medical-devices/device-advice-comprehensive-regulatory-assistance/human-factors-and-medical-devices), [FDA usability-engineering guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/applying-human-factors-and-usability-engineering-medical-devices)).

**Applied decision:** the core decision object answers action, time, change, reliability, next observation and audit consequence in one stable reading order. Accept/modify/override provide immediate feedback and cannot silently fail.

### 5. Density requires hierarchy and accessible mechanics

Linear's 2026 interface refresh argues that information-rich tools should not give every element equal visual weight; navigation should recede behind the task ([Linear design refresh](https://linear.app/now/behind-the-latest-design-refresh)). Carbon's current table guidance requires accessible names, keyboard-operable sort headers and programmatic sort state, while IBM recommends filters/pagination and fewer per-row controls to reduce keyboard effort ([Carbon data-table accessibility](https://preview.carbondesignsystem.com/building-blocks/core/components/data-table/accessibility), [IBM accessible visual design](https://www.ibm.com/able/toolkit/design/visual/)).

**Applied decision:** navigation is visually quiet, the selected row and current action dominate, the table exposes one primary row action, filters reduce noise, and sorting/selection are keyboard-operable.

### 6. Status needs redundant coding

WCAG 2.2 requires that color not be the only carrier of meaning, establishes text/non-text contrast and visible-focus requirements, and allows two-dimensional scrolling for genuinely complex data tables ([W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)). NHS England targets WCAG 2.2 AA and expects keyboard, zoom/reflow and screen-reader usability ([NHS accessibility statement](https://www.nhs.uk/accessibility-statement/)).

**Applied decision:** every urgency/status has text plus shape/icon, charts have textual equivalents, focus is high-contrast, and responsive behavior preserves patient context instead of merely shrinking type.

## Chosen direction: Deadline Board + Patient Inspector

```text
SITE / SCENARIO / CLOCK / CAPACITY TRUTH
┌──────────┬────────────────────────────────────┬─────────────────────┐
│ quiet    │ QUEUE                              │ SELECTED PATIENT    │
│ product  │ ranked by Clinical Slack           │ action + by when    │
│ nav      │                                    │ slack line          │
│          │ [patient rows with trajectory]     │ what changed        │
│          │                                    │ uncertainty + NBO   │
│          │                                    │ accept/modify/over. │
└──────────┴────────────────────────────────────┴─────────────────────┘
```

## Alternatives considered

- **Tile-based command center:** visually familiar in hospital operations but makes the unit of work a widget rather than a patient deadline. Retained only for the separate surge/evaluation views.
- **Patient journey timeline as home:** strong for one case, weak for maintaining waiting-room situation awareness. Retained inside the inspector.
- **Risk-score dashboard:** easiest to build and explain, but generic, easy to over-trust and misaligned with the core novelty. Rejected.

## Distinctive product signatures

1. **Clinical Slack line:** visually joins clinical need and operational feasibility; negative Slack is shown as a capacity conflict, not merely a higher score.
2. **Action Window as the primary number:** phrased as “recommended within,” never as a guaranteed safe deadline.
3. **Uncertainty that creates work:** Safe Mode and Next Best Observation turn uncertainty into a specific reassessment action.
4. **Deterioration as an observable queue event:** a new vital sign visibly changes trajectory, deadline and board position while preserving before/after evidence.
5. **Human-decision trail:** accept, modify and override are product states linked to the exact recommendation, reason and component versions.

## Research limits

Public product pages and published screenshots reveal information hierarchy and product claims but do not establish the complete workflows, alarm behavior or usability of proprietary systems. Those examples are treated as precedent, not proof. The TriageLoop interface still requires task-based clinician usability testing before any real clinical claim.
