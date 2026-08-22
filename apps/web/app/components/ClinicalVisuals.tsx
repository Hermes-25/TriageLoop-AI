import { AlertTriangle, Check, CircleHelp, ShieldAlert } from "lucide-react";

export function formatAction(action: string) {
  const labels: Record<string, string> = {
    immediate_review: "Immediate review",
    reassess: "Reassess",
    escalate_priority: "Escalate priority",
    continue_monitored_wait: "Continue monitored wait",
    safe_mode_review: "Safe Mode review",
  };
  return labels[action] ?? action.replaceAll("_", " ");
}

export function formatMinutes(value: number | null | undefined, signed = false) {
  if (value == null) return "Unknown";
  const rounded = Math.round(value);
  if (signed && rounded > 0) return `+${rounded}m`;
  return `${rounded}m`;
}

export function formatActionWindow(value: number | null | undefined) {
  if (value == null) return "Unknown";
  if (value <= 0) return "Now";
  if (value <= 5) return "≤5m";
  if (value <= 15) return "≤15m";
  if (value <= 30) return "≤30m";
  return `~${Math.round(value / 5) * 5}m`;
}

export function formatEta(value: number | null | undefined) {
  if (value == null) return "Unknown";
  if (value <= 0) return "Now";
  return `~${Math.round(value)}m`;
}

export function StatusMark({ kind, label }: { kind: "critical" | "warning" | "safe" | "info"; label: string }) {
  const Icon = kind === "critical" ? ShieldAlert : kind === "warning" ? AlertTriangle : kind === "safe" ? Check : CircleHelp;
  return (
    <span className={`status-mark ${kind}`}>
      <Icon size={13} strokeWidth={2.2} aria-hidden="true" />
      {label}
    </span>
  );
}

export function RiskSparkline({ values, conflict = false }: { values: number[]; conflict?: boolean }) {
  const width = 86;
  const height = 30;
  const points = values.map((value, index) => {
    const x = 3 + (index * (width - 6)) / Math.max(1, values.length - 1);
    const y = height - 3 - value * (height - 6);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  return (
    <span className="spark-wrap" aria-label={`Estimated critical risk at 5, 15, 30 and 60 minutes: ${values.map((v) => `${Math.round(v * 100)}%`).join(", ")}`}>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-hidden="true">
        <path d={`M3 ${height - 3} H${width - 3}`} className="spark-axis" />
        <polyline points={points} className={conflict ? "spark-line conflict" : "spark-line"} />
        {values.map((value, index) => {
          const [cx, cy] = points.split(" ")[index].split(",");
          return <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="2" className={conflict ? "spark-dot conflict" : "spark-dot"} />;
        })}
      </svg>
    </span>
  );
}

export function SlackLine({ deadline, eta, slack, conflict }: { deadline: number; eta: number | null; slack: number | null; conflict: boolean }) {
  const predicted = eta ?? deadline;
  const limit = Math.max(deadline, predicted, 10) * 1.12;
  const deadlinePosition = Math.min(92, (deadline / limit) * 100);
  const etaPosition = Math.min(96, (predicted / limit) * 100);
  return (
    <div className={`slack-line ${conflict ? "is-conflict" : ""}`} aria-label={`Recommended action window ${formatActionWindow(deadline)}. Predicted action ${formatEta(eta)}. Clinical Slack ${formatMinutes(slack, true)}${conflict ? ", capacity conflict" : ""}.`}>
      <div className="slack-track" aria-hidden="true">
        <span className="deadline-zone" style={{ width: `${deadlinePosition}%` }} />
        <span className="deadline-tick" style={{ left: `${deadlinePosition}%` }} />
        <span className="eta-dot" style={{ left: `${etaPosition}%` }} />
      </div>
      <div className="slack-labels">
        <span>Now</span>
        <strong>{conflict ? `${formatMinutes(slack)} conflict` : `${formatMinutes(slack, true)} slack`}</strong>
      </div>
    </div>
  );
}
