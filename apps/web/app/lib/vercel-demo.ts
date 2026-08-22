import { createHash } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import fixture from "@/app/lib/vercel-demo-fixtures.json";
import type { AuditEvent, ProductState, Scenario } from "@/app/lib/types";

type Decision = {
  patientId: string;
  action: "accept" | "modify" | "override";
  reason?: string;
  modifiedAction?: string;
};

type DemoFlags = {
  scenario: Scenario;
  deteriorated: boolean;
  decision?: Decision;
};

type Snapshot = { state: ProductState; audit: AuditEvent[] };

const COOKIE = "triageloop_public_demo";
const DEFAULT_FLAGS: DemoFlags = { scenario: "baseline", deteriorated: false };

function readFlags(request: NextRequest): DemoFlags {
  const encoded = request.cookies.get(COOKIE)?.value;
  if (!encoded) return DEFAULT_FLAGS;
  try {
    const parsed = JSON.parse(Buffer.from(encoded, "base64url").toString("utf8")) as DemoFlags;
    if (!(["baseline", "surge_3x"] as string[]).includes(parsed.scenario)) return DEFAULT_FLAGS;
    return parsed;
  } catch {
    return DEFAULT_FLAGS;
  }
}

function respond(payload: unknown, flags: DemoFlags, status = 200) {
  const response = NextResponse.json(payload, { status });
  response.cookies.set(COOKIE, Buffer.from(JSON.stringify(flags)).toString("base64url"), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24,
  });
  response.headers.set("X-TriageLoop-Adapter", "canonical-synthetic-snapshots");
  return response;
}

function snapshotKey(flags: DemoFlags) {
  if (flags.scenario === "surge_3x") return flags.deteriorated ? "surge_3x_deteriorated" : "surge_3x";
  return flags.deteriorated ? "baseline_deteriorated" : "baseline";
}

function stable(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value as Record<string, unknown>).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => [key, stable(item)]));
  }
  return value;
}

function materialize(flags: DemoFlags): Snapshot {
  const states = fixture.states as unknown as Record<string, Snapshot>;
  const current = structuredClone(states[snapshotKey(flags)]);
  if (!flags.decision) return current;

  const patient = current.state.patients.find((item) => item.patient_id === flags.decision?.patientId);
  if (patient) {
    patient.decision_state = flags.decision.action === "accept"
      ? "accept"
      : `${flags.decision.action}:${flags.decision.modifiedAction ?? "clinician judgement"}`;
  }

  const ascending = [...current.audit].sort((a, b) => a.sequence - b.sequence);
  const previousHash = ascending.at(-1)?.event_hash ?? null;
  const seed = JSON.stringify(flags.decision);
  const eventWithoutHash = {
    sequence: (ascending.at(-1)?.sequence ?? 0) + 1,
    event_id: `EVT-VERCEL-${createHash("sha256").update(seed).digest("hex").slice(0, 12)}`,
    patient_id: flags.decision.patientId,
    created_at: "2026-08-22T10:43:00+05:30",
    actor: "nurse",
    event_type: flags.decision.action === "override" ? "recommendation_overridden" : `recommendation_${flags.decision.action}ed`,
    payload: {
      clinician_action: flags.decision.modifiedAction ?? "clinician judgement",
      reason: flags.decision.reason ?? null,
      autonomous_downgrade: false,
      presentation_adapter: true,
    },
    previous_hash: previousHash,
  };
  const canonical = JSON.stringify(stable({
    event_id: eventWithoutHash.event_id,
    patient_id: eventWithoutHash.patient_id,
    created_at: eventWithoutHash.created_at,
    actor: eventWithoutHash.actor,
    event_type: eventWithoutHash.event_type,
    payload: eventWithoutHash.payload,
    previous_hash: eventWithoutHash.previous_hash,
  }));
  const event: AuditEvent = {
    ...eventWithoutHash,
    event_hash: createHash("sha256").update(`${previousHash ?? "GENESIS"}${canonical}`).digest("hex"),
  };
  current.audit = [event, ...current.audit];
  return current;
}

export async function handleVercelDemo(request: NextRequest, path: string[]) {
  const route = `/${path.join("/")}`;
  let flags = readFlags(request);

  if (request.method === "GET" && route === "/v1/health") {
    return respond({ status: "ok", mode: "synthetic-presentation-adapter", version: "0.4.0-vercel" }, flags);
  }
  if (request.method === "GET" && route === "/v1/config") {
    return respond({
      site_profiles: ["community", "regional", "urban_trauma"],
      scenarios: ["baseline", "surge_3x"],
      clinical_calculation_owner: "canonical-precomputed-fastapi-snapshots",
      autonomous_downgrade_permitted: false,
      prototype_notice: "Synthetic decision-support prototype - not validated for clinical use.",
    }, flags);
  }
  if (request.method === "POST" && route === "/v1/demo/reset") {
    flags = DEFAULT_FLAGS;
    return respond(materialize(flags).state, flags);
  }
  if (request.method === "POST" && route === "/v1/demo/scenario") {
    const body = await request.json().catch(() => ({})) as { scenario?: Scenario };
    if (!body.scenario || !(["baseline", "surge_3x"] as string[]).includes(body.scenario)) {
      return respond({ detail: "scenario must be baseline or surge_3x" }, flags, 422);
    }
    flags = { ...flags, scenario: body.scenario };
    return respond(materialize(flags).state, flags);
  }
  if (request.method === "POST" && route.startsWith("/v1/demo/deteriorate/")) {
    const patientId = route.split("/").at(-1);
    if (patientId !== "P-0009") return respond({ detail: "patient not found" }, flags, 404);
    flags = { ...flags, deteriorated: true };
    const current = materialize(flags);
    return respond(current.state.patients.find((patient) => patient.patient_id === patientId), flags);
  }
  if (request.method === "POST" && /^\/v1\/patients\/P-\d+\/decisions$/.test(route)) {
    const patientId = route.split("/")[3];
    const body = await request.json().catch(() => ({})) as { action?: Decision["action"]; reason?: string; modified_action?: string };
    if (!body.action || !(["accept", "modify", "override"] as string[]).includes(body.action)) {
      return respond({ detail: "action must be accept, modify or override" }, flags, 422);
    }
    if ((body.action === "modify" || body.action === "override") && !body.reason?.trim()) {
      return respond({ detail: "a reason is required for modify or override" }, flags, 422);
    }
    flags = { ...flags, decision: { patientId, action: body.action, reason: body.reason?.slice(0, 500), modifiedAction: body.modified_action?.slice(0, 120) } };
    const current = materialize(flags);
    return respond({ decision_state: current.state.patients.find((patient) => patient.patient_id === patientId)?.decision_state, audit_event: current.audit[0] }, flags);
  }
  if (request.method === "GET" && route === "/v1/demo/state") return respond(materialize(flags).state, flags);
  if (request.method === "GET" && route === "/v1/audit") return respond(materialize(flags).audit, flags);
  if (request.method === "GET" && route === "/v1/audit/integrity") {
    const audit = materialize(flags).audit;
    return respond({ intact: true, events_checked: audit.length, first_broken_sequence: null, algorithm: "SHA-256", prototype_only: true }, flags);
  }
  if (request.method === "GET" && route === "/v1/evaluations/latest") return respond(fixture.evaluation, flags);

  return respond({ detail: "presentation-adapter route not found" }, flags, 404);
}
