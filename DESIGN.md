# TriageLoop Product Design System

## Experience statement

An ED control desk at 02:00: bright enough to read instantly, quiet enough not to compete with the room, and precise enough that a missed deadline is impossible to mistake for decoration.

## Direction

The primary surface is a **clinical deadline board**, not a dashboard. It uses a stable operations shell, a comparison-first queue table and a persistent patient inspector. Density comes from alignment and typography rather than nested cards. The distinctive visual signature is a horizontal **Slack line** that joins the patient's Action Window, predicted time to action and capacity conflict in one readable object.

## Color strategy

Restrained. Neutral white and cool-ink surfaces carry the workload. A deep berry brand color anchors selection and primary actions while remaining separate from clinical red. Clinical states use a limited semantic set with text and icon reinforcement.

```css
:root {
  --bg: oklch(1 0 0);
  --surface: oklch(0.973 0.004 330);
  --surface-raised: oklch(0.992 0.002 330);
  --ink: oklch(0.19 0.018 292);
  --ink-soft: oklch(0.43 0.018 292);
  --line: oklch(0.89 0.008 292);
  --brand: oklch(0.45 0.15 330);
  --brand-strong: oklch(0.36 0.14 330);
  --brand-soft: oklch(0.95 0.025 330);
  --critical: oklch(0.49 0.19 25);
  --critical-soft: oklch(0.95 0.035 25);
  --warning: oklch(0.66 0.14 75);
  --warning-soft: oklch(0.96 0.04 75);
  --safe: oklch(0.49 0.11 158);
  --safe-soft: oklch(0.95 0.03 158);
  --info: oklch(0.48 0.12 245);
  --info-soft: oklch(0.95 0.03 245);
}
```

## Typography

- Interface: Segoe UI Variable / system sans-serif fallback.
- Clinical times, patient IDs and tabular measurements: Cascadia Mono / system monospace fallback with tabular numerals.
- Compact product scale: 12, 13, 14, 16, 18, 22 and 28px. No display typography in operational views.
- Sentence case throughout. Uppercase is limited to compact machine states such as `SAFE MODE` where scanning benefits.

## Layout

- Desktop-first working viewport: 1440×900, usable from 1280px.
- Persistent 166px labelled navigation rail at wide desktop, collapsing to a 68px icon rail below 1280px; 52px operational context bar.
- Board uses a two-column split: fluid patient queue plus a 400–440px patient inspector.
- Queue rows are 58–68px high and expose one row-level action: select/open. Actions live in the inspector to minimize keyboard and visual clutter.
- At tablet and narrow widths the product becomes a deliberate queue-first drill-down: selecting a patient opens a full-height inspector with an explicit return to the queue. The data table remains horizontally scrollable where its two-dimensional comparison is essential.

## Core components

### Patient queue row

Contains rank, pseudonymous patient identity, age band, complaint, current level, action, Action Window, ETA, Clinical Slack, uncertainty and latest change. Selected and focused states use brand color; clinical urgency never depends on selection color.

### Slack line

A compact, accessible visualization of two times on one bounded track: clinical deadline and predicted action. Negative Slack places ETA beyond the deadline and adds an explicit `Capacity conflict` label. A text equivalent always accompanies the graphic.

### Patient inspector

Progressive detail in one stable order: recommended action → deadline/ETA/slack → trajectory → reasons/uncertainty → Next Best Observation → clinician decision. No nested cards; sections use dividers and spacing.

### Operational state banner

Shows the site, scenario, simulated time, connection state and the one system-level capacity message. It is never a carousel of alerts.

### Decision bar

Accept is the primary action. Modify and Override reveal inline reason fields. State-changing actions require explicit confirmation text and append to the audit trail; they do not use an interruptive modal unless persistence fails.

## Motion

- Row reordering after deterioration: 200ms ease-out with a brief positional highlight; reduced-motion mode applies the final order instantly and announces the change in a live region.
- Inspector selection: 160ms opacity transition; no sliding panel on desktop.
- State confirmation: 180ms background emphasis then settles; always paired with text.
- No decorative or orchestrated page-load animation.

## Product boundaries

Every clinical surface displays `Synthetic decision-support prototype — not validated for clinical use`. The interface never says “safe until,” never hides Safe Mode, and never implies that queue optimization creates capacity.
