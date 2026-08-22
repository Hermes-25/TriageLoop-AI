"""FastAPI product surface for the TriageLoop TL-04 prototype."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .product_store import ProductStore
from .schemas import PatientState


class ScenarioRequest(BaseModel):
    scenario: Literal["baseline", "surge_3x"]


class DecisionRequest(BaseModel):
    action: Literal["accept", "modify", "override"]
    reason: str | None = Field(default=None, max_length=500)
    modified_action: str | None = Field(default=None, max_length=120)


def create_app(database_path: Path | None = None) -> FastAPI:
    app = FastAPI(
        title="TriageLoop API",
        version="0.4.0",
        description="Synthetic, nurse-led decision-support prototype. Not for clinical use.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in os.getenv("TRIAGELOOP_CORS_ORIGINS", "http://localhost:3000").split(",")],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    store = ProductStore(database_path)
    app.state.store = store

    @app.get("/v1/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "synthetic-prototype", "version": "0.4.0"}

    @app.get("/v1/config")
    def config() -> dict[str, object]:
        return {
            "site_profiles": ["community", "regional", "urban_trauma"],
            "scenarios": ["baseline", "surge_3x"],
            "clinical_calculation_owner": "api",
            "autonomous_downgrade_permitted": False,
            "prototype_notice": "Synthetic decision-support prototype — not validated for clinical use.",
        }

    @app.get("/v1/demo/state")
    def demo_state() -> dict[str, object]:
        return store.state()

    @app.post("/v1/demo/reset")
    def reset_demo() -> dict[str, object]:
        return store.reset()

    @app.post("/v1/demo/scenario")
    def set_scenario(request: ScenarioRequest) -> dict[str, object]:
        return store.set_scenario(request.scenario)

    @app.post("/v1/demo/deteriorate/{patient_id}")
    def deteriorate(patient_id: str) -> dict[str, object]:
        try:
            return store.deteriorate(patient_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="patient not found") from error

    @app.get("/v1/patients")
    def patients() -> list[dict[str, object]]:
        return store.state()["patients"]

    @app.post("/v1/intake/manual", status_code=201)
    def manual_intake(patient_state: PatientState) -> dict[str, object]:
        try:
            return store.add_manual_patient(patient_state)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/v1/patients/{patient_id}")
    def patient(patient_id: str) -> dict[str, object]:
        try:
            return store.patient(patient_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="patient not found") from error

    @app.get("/v1/patients/{patient_id}/recommendation")
    def recommendation(patient_id: str) -> dict[str, object]:
        return patient(patient_id)["recommendation"]

    @app.post("/v1/patients/{patient_id}/decisions")
    def decision(patient_id: str, request: DecisionRequest) -> dict[str, object]:
        try:
            return store.record_decision(patient_id, request.action, request.reason, request.modified_action)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="patient not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/v1/patients/{patient_id}/audit")
    def patient_audit(patient_id: str) -> list[dict[str, object]]:
        return store.audit(patient_id=patient_id)

    @app.get("/v1/audit")
    def audit(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, object]]:
        return store.audit(limit=limit)

    @app.get("/v1/audit/integrity")
    def audit_integrity() -> dict[str, object]:
        return store.verify_audit_chain()

    @app.get("/v1/evaluations/latest")
    def evaluation() -> dict[str, object]:
        return store.evaluation()

    @app.get("/v1/events/stream")
    async def event_stream() -> StreamingResponse:
        async def events():
            yield f"event: state\ndata: {json.dumps(store.state())}\n\n"
            while True:
                await asyncio.sleep(20)
                yield "event: heartbeat\ndata: {}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run("triageloop.api:app", host="127.0.0.1", port=8000, reload=False)
