# Docker for beginners: what it does for TriageLoop

You do not need to understand containers to run the prototype. This page explains the idea and the few commands that matter.

## The simple mental model

Imagine sending someone a complex recipe. Without Docker, they must separately find the correct oven, ingredients and utensils—and compatible versions of each. With Docker, you send two sealed, labelled kitchen stations that already contain the required environment.

TriageLoop has two stations:

1. **`api` — the decision service.** Python runs the safety rules, trajectory model, uncertainty checks, Queue Twin, decisions and audit persistence.
2. **`web` — the product interface.** Next.js renders the Deadline Board, patient inspector, surge, evidence and audit screens.

`compose.yaml` describes how those stations connect. Docker builds them from `infra/api.Dockerfile` and `infra/web.Dockerfile`, starts the API first, waits for its health check, and then starts the web interface.

## Why this matters to a competition judge

- **One repeatable command:** the judge does not need to install Python packages and Node packages manually.
- **Version consistency:** the prototype uses the same Python and Node foundations we tested.
- **Isolation:** project dependencies do not overwrite software already installed on the judge's computer.
- **Evidence of a real product:** the browser talks to the live Python service, not merely to a static mock.
- **Restart behavior:** the named Docker volume preserves the prototype audit database across ordinary container restarts.

Docker does not make the prototype clinically validated, secure for hospital deployment or automatically scalable. It makes the software package reproducible.

## Run it

Install and start Docker Desktop, open a terminal in the repository folder, and run:

```bash
docker compose up --build -d
```

Then open:

- Product: <http://localhost:3000/board>
- API health: <http://localhost:8000/v1/health>

Expected health response:

```json
{"status":"ok","mode":"synthetic-prototype","version":"0.4.0"}
```

## Stop, restart and reset

Stop the running containers while preserving the audit volume:

```bash
docker compose down
```

Start them again:

```bash
docker compose up -d
```

Use **Reset demo** inside the product to return to the deterministic baseline. This is different from deleting the Docker volume: reset is a supported product action that creates a fresh, valid baseline audit event.

## What our release gate proved

The verified Windows/WSL 2 run built both images, returned a healthy API and HTTP 200 board, completed the eight-stage browser journey with zero browser errors, preserved five audit events and the newest SHA-256 link across restart, and restored one intact baseline event after reset.

Machine-readable evidence is stored in [`artifacts/release/tl07-docker-verification.json`](../artifacts/release/tl07-docker-verification.json).

## Common problems

| Symptom | Meaning | First action |
|---|---|---|
| `docker` is not recognized | Docker Desktop is missing or not on `PATH` | Install/start Docker Desktop, then reopen the terminal |
| Cannot connect to Docker engine | Docker Desktop is installed but its Linux engine is not ready | Start Docker Desktop and wait until it reports running |
| Port 3000 or 8000 is already in use | Another local program owns the port | Stop that program or change the left-hand port in `compose.yaml` |
| Web waits for API | The API health check has not passed | Run `docker compose logs api` |
| UI container exits | Inspect the runtime error | Run `docker compose logs web` |

No real patient information should ever be entered into this prototype.
