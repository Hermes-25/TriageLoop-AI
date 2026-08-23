"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, useTransition } from "react";
import { productApi } from "@/app/lib/api";
import type { Patient, ProductState, Scenario } from "@/app/lib/types";

type DecisionPayload = { action: string; reason?: string; modified_action?: string };

interface ProductContextValue {
  state: ProductState | null;
  selectedPatient: Patient | null;
  selectedId: string | null;
  loading: boolean;
  pending: boolean;
  degraded: boolean;
  error: string | null;
  announcement: string;
  selectPatient: (id: string) => void;
  refresh: () => Promise<void>;
  setScenario: (scenario: Scenario) => void;
  runDeterioration: () => void;
  resetDemo: () => void;
  simulateOutage: () => void;
  restoreService: () => Promise<void>;
  recordDecision: (patientId: string, payload: DecisionPayload) => Promise<void>;
}

const ProductContext = createContext<ProductContextValue | null>(null);

export function ProductProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<ProductState | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [degraded, setDegraded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [announcement, setAnnouncement] = useState("");
  const [pending, startTransition] = useTransition();

  const refresh = useCallback(async () => {
    const loadingStartedAt = performance.now();
    setError(null);
    try {
      const next = await productApi.state();
      setState(next);
      setDegraded(false);
      setSelectedId((current) => current ?? next.patients[0]?.patient_id ?? null);
    } catch (reason) {
      setDegraded(true);
      setError(reason instanceof Error ? reason.message : "Unable to load the clinical board.");
    } finally {
      const remainingDisplayTime = 520 - (performance.now() - loadingStartedAt);
      if (remainingDisplayTime > 0) {
        await new Promise((resolve) => window.setTimeout(resolve, remainingDisplayTime));
      }
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const mutate = useCallback((operation: () => Promise<ProductState>, message: (result: ProductState) => string) => {
    if (degraded) {
      setError("Decision service is degraded. Live queue recalculation is paused; use fixed category deadlines and local escalation protocol.");
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        const result = await operation();
        setState(result);
        setAnnouncement(message(result));
      } catch (reason) {
        setDegraded(true);
        setError(reason instanceof Error ? reason.message : "The action could not be completed.");
      }
    });
  }, [degraded]);

  const setScenario = useCallback((scenario: Scenario) => {
    mutate(() => productApi.scenario(scenario), (result) => `${result.scenario_label} scenario applied. Queue feasibility recalculated.`);
  }, [mutate]);

  const runDeterioration = useCallback(() => {
    if (degraded) {
      setError("A new observation cannot be processed while the decision service is degraded. Escalate through the local clinical workflow.");
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        await productApi.deteriorate("P-0009");
        const result = await productApi.state();
        setState(result);
        setSelectedId("P-0009");
        setAnnouncement("New reassessment recorded for P-0009. Patient moved to queue position 2 with negative Clinical Slack.");
      } catch (reason) {
        setDegraded(true);
        setError(reason instanceof Error ? reason.message : "The deterioration event could not be completed.");
      }
    });
  }, [degraded]);

  const resetDemo = useCallback(() => {
    mutate(productApi.reset, () => "Demo reset to the baseline waiting room.");
  }, [mutate]);

  const simulateOutage = useCallback(() => {
    setDegraded(true);
    setError(null);
    setAnnouncement("Decision service degraded. Live model and queue estimates are paused; category deadlines and local protocol remain authoritative.");
  }, []);

  const restoreService = useCallback(async () => {
    setError(null);
    try {
      const next = await productApi.state();
      setState(next);
      setDegraded(false);
      setSelectedId((current) => current ?? next.patients[0]?.patient_id ?? null);
      setAnnouncement("Decision service restored. Live recommendations and queue feasibility refreshed.");
    } catch (reason) {
      setDegraded(true);
      setError(reason instanceof Error ? reason.message : "The decision service is still unavailable.");
      setAnnouncement("Restore check failed. Continue the local downtime workflow.");
    }
  }, []);

  const recordDecision = useCallback(async (patientId: string, payload: DecisionPayload) => {
    if (degraded) {
      const outageError = new Error("Digital decision recording is unavailable in degraded mode. Use the local downtime record and reconcile after restoration.");
      setError(outageError.message);
      throw outageError;
    }
    setError(null);
    try {
      await productApi.decision(patientId, payload);
      const result = await productApi.state();
      setState(result);
      setAnnouncement(`${payload.action} recorded for ${patientId}. The audit chain has been updated.`);
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : "The clinician decision could not be recorded.";
      setError(message);
      throw reason;
    }
  }, [degraded]);

  const selectedPatient = useMemo(
    () => state?.patients.find((patient) => patient.patient_id === selectedId) ?? state?.patients[0] ?? null,
    [selectedId, state],
  );

  const value = useMemo<ProductContextValue>(() => ({
    state,
    selectedPatient,
    selectedId,
    loading,
    pending,
    degraded,
    error,
    announcement,
    selectPatient: setSelectedId,
    refresh,
    setScenario,
    runDeterioration,
    resetDemo,
    simulateOutage,
    restoreService,
    recordDecision,
  }), [state, selectedPatient, selectedId, loading, pending, degraded, error, announcement, refresh, setScenario, runDeterioration, resetDemo, simulateOutage, restoreService, recordDecision]);

  return (
    <ProductContext.Provider value={value}>
      <p className="sr-only" aria-live="polite">{announcement}</p>
      {children}
    </ProductContext.Provider>
  );
}

export function useProduct() {
  const value = useContext(ProductContext);
  if (!value) throw new Error("useProduct must be used inside ProductProvider");
  return value;
}
