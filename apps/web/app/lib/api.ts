import type { AuditEvent, AuditIntegrity, Evaluation, ProductState } from "@/app/lib/types";

const ROOT = "/api/triageloop/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${ROOT}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const productApi = {
  state: () => request<ProductState>("/demo/state"),
  reset: () => request<ProductState>("/demo/reset", { method: "POST", body: "{}" }),
  scenario: (scenario: ProductState["scenario"]) =>
    request<ProductState>("/demo/scenario", { method: "POST", body: JSON.stringify({ scenario }) }),
  deteriorate: (patientId = "P-0009") =>
    request(`/demo/deteriorate/${patientId}`, { method: "POST", body: "{}" }),
  decision: (patientId: string, body: { action: string; reason?: string; modified_action?: string }) =>
    request(`/patients/${patientId}/decisions`, { method: "POST", body: JSON.stringify(body) }),
  evaluation: () => request<Evaluation>("/evaluations/latest"),
  audit: () => request<AuditEvent[]>("/audit?limit=200"),
  auditIntegrity: () => request<AuditIntegrity>("/audit/integrity"),
};
