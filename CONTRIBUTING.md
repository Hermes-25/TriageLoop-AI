# Contributing to TriageLoop.ai

Thank you for helping improve the research prototype. Contributions are welcome when they preserve the project's safety boundaries, reproducibility and claim discipline.

## Before opening a change

1. Read [`PRODUCT.md`](PRODUCT.md), [`DESIGN.md`](DESIGN.md) and [`docs/clinical-safety-contract.md`](docs/clinical-safety-contract.md).
2. Use only synthetic or appropriately deidentified test data. Never submit personal or patient information.
3. Open an issue for changes that alter clinical rules, Action Window logic, uncertainty handling, queue policy, reported metrics or public claims.
4. Keep deterministic safety rules ahead of model output. A model may constrain an Action Window; it may not suppress a hard red flag or autonomously downgrade a patient.

## Development checks

Python changes:

```bash
python -m pip install -e services/api
python -m unittest discover -s tests -p "test_*.py" -v
```

Web changes:

```bash
cd apps/web
corepack enable
pnpm install --frozen-lockfile
pnpm typecheck
pnpm build
```

Container contract:

```bash
docker compose config --quiet
docker compose up --build -d
```

Confirm `http://localhost:8000/v1/health` and `http://localhost:3000/board`, then stop with `docker compose down`.

## Pull-request expectations

- Explain the user or research problem being addressed.
- List tests and evidence produced.
- Identify any changed assumptions, safety boundaries or claims.
- Add or update documentation with the code.
- Keep secrets, generated caches, local databases and real patient data out of commits.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md).
