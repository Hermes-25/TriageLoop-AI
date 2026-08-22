# TriageLoop Web

Next.js App Router product interface for the nurse waiting-room board, patient decision inspector, surge view, evaluation evidence and audit trail.

In the local and Docker modes, the FastAPI service remains the source of all quantitative decisions. The browser uses the same-origin proxy under `/api/triageloop/*`; set `TRIAGELOOP_API_URL` to change the upstream API (default `http://127.0.0.1:8000`).

On Vercel, the route handler deliberately switches to a synthetic presentation adapter backed by canonical snapshots exported from FastAPI. It preserves the deterministic reset, deterioration, surge, override, audit, evidence and capacity story with an HTTP-only session cookie, while accepting no real patient data. Set `TRIAGELOOP_PRESENTATION_ADAPTER=1` to exercise this mode locally. This hosted path is a jury preview, not the live Python decision service or a clinical deployment.

Production preview: <https://triageloop-ai.vercel.app/board>

```powershell
pnpm dev
```

This is a synthetic research prototype and is not validated for clinical use.
