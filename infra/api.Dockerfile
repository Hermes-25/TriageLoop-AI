FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY services/api/pyproject.toml /app/services/api/pyproject.toml
COPY services/api/triageloop /app/services/api/triageloop
RUN python -m pip install --no-cache-dir -e /app/services/api

COPY artifacts /app/artifacts
COPY data /app/data
RUN mkdir -p /app/artifacts/reports

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "triageloop.api:app", "--app-dir", "/app/services/api", "--host", "0.0.0.0", "--port", "8000"]
