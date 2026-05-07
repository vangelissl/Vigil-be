FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/

RUN pip install .

COPY vigil-tasks /app/vigil-tasks
RUN pip install /app/vigil-tasks

COPY alembic/ alembic/
COPY alembic.ini .

EXPOSE 8000

CMD ["uvicorn", "vigil.main:app", "--host", "0.0.0.0", "--port", "8000"]
