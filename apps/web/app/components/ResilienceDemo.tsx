"use client";

import { CloudOff, RefreshCw } from "lucide-react";
import { useProduct } from "@/app/components/ProductProvider";

export function ResilienceDemo() {
  const { degraded, pending, simulateOutage, restoreService } = useProduct();
  return (
    <section className={`resilience-demo ${degraded ? "active" : ""}`} aria-labelledby="resilience-heading">
      <CloudOff size={20} aria-hidden="true" />
      <div>
        <h2 id="resilience-heading">Decision-service fallback</h2>
        <p>{degraded ? "Degraded mode is active: the last verified board is retained while live model, ETA and digital decision recording are paused." : "Demonstrate that a service outage produces an explicit rules-and-category fallback—not a blank screen or silent stale estimate."}</p>
      </div>
      {degraded ? (
        <button className="button secondary" type="button" disabled={pending} onClick={() => void restoreService()}><RefreshCw size={15} aria-hidden="true" /> Restore service</button>
      ) : (
        <button className="button secondary" type="button" onClick={simulateOutage}><CloudOff size={15} aria-hidden="true" /> Simulate outage</button>
      )}
    </section>
  );
}
