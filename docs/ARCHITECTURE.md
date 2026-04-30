# Vigil — Architecture Overview

## Stack

| Layer                   | Technology                                      |
| ----------------------- | ----------------------------------------------- |
| API                     | FastAPI (async)                                 |
| Database                | PostgreSQL via SQLAlchemy 2.0 (async) + Alembic |
| Object Storage          | MinIO (local Docker)                            |
| Cache / Message Broker  | Redis                                           |
| Task Queue              | Celery                                          |
| ML Framework            | MMAction2 (C3D / I3D) — isolated service        |
| Shared Task Definitions | `vigil-tasks` (internal package)                |

---

## Architectural Style

The project follows **Hexagonal Architecture (Ports & Adapters)**, applied per module.

```
┌──────────────────────────────────────────────────────┐
│  Presentation Layer  (Routers, Request/Response DTOs) │
├──────────────────────────────────────────────────────┤
│  Application Layer   (Use Cases, Services)            │
├──────────────────────────────────────────────────────┤
│  Domain Layer        (Entities, Value Objects, Rules) │
├──────────────────────────────────────────────────────┤
│  Infrastructure Layer (DB, MinIO, Redis, ML Adapter)  │
└──────────────────────────────────────────────────────┘
```

**Dependency rule:** inner layers never import from outer layers.

Each module contains the full vertical slice:

```
modules/<module>/
├── ports.py          # Abstract interfaces (ABCs / Protocols) — contracts for infra and cross-module calls
├── domain/           # Entities, value objects, domain exceptions. Zero framework dependencies.
├── application/      # Use cases and orchestration. Depends only on domain and ports.
├── infrastructure/   # Concrete implementations: repositories, storage clients, ML adapter.
└── presentation/     # FastAPI routers and Pydantic schemas.
```

Modules **never depend on each other's internals**. Cross-module communication happens exclusively through ports.

---

## Project Structure

The repository is organized as a monorepo with three top-level packages:

```
.
├── docker-compose.yml
├── pyproject.toml
│
├── src/                          # Main FastAPI application
│   └── vigil/
│       ├── core/
│       │   └── config.py         # Settings via pydantic-settings
│       │
│       ├── modules/
│       │   ├── auth/
│       │   │   ├── ports.py
│       │   │   ├── domain/       # (no User entity — owned by users module)
│       │   │   ├── application/  # AuthService: register, login, refresh, logout
│       │   │   ├── infrastructure/
│       │   │   └── presentation/ # POST /auth/register, /login, /refresh, /logout
│       │   │
│       │   ├── users/
│       │   │   ├── ports.py      # UserRepository (ABC)
│       │   │   ├── domain/       # User entity, value objects, exceptions
│       │   │   ├── application/  # UserService
│       │   │   ├── infrastructure/
│       │   │   └── presentation/ # GET /users/me, PATCH /users/me
│       │   │
│       │   ├── videos/
│       │   │   ├── ports.py      # VideoRepository (ABC) — consumed by analysis module
│       │   │   ├── domain/       # Video entity, VideoStatus enum, exceptions
│       │   │   ├── application/  # VideoService: upload, list, get_by_id
│       │   │   ├── infrastructure/
│       │   │   └── presentation/ # POST /videos/upload, GET /videos, GET /videos/{id}
│       │   │
│       │   └── analysis/
│       │       ├── ports.py      # VideoRepository (imported from videos/ports.py)
│       │       ├── domain/       # Analysis entity, AnalysisStatus enum, ClassificationResult
│       │       ├── application/  # AnalysisService: trigger, get_result
│       │       ├── infrastructure/
│       │       └── presentation/ # POST /analyses, GET /analyses/{id}, GET /analyses
│       │
│       ├── security/
│       │   ├── token.py          # TokenService: sign, verify JWT
│       │   └── dependencies.py   # get_current_user FastAPI dependency
│       │
│       ├── shared/               # Shared utilities (base entities, pagination, etc.)
│       │
│       ├── database/
│       │   ├── session.py        # Async engine + sessionmaker
│       │   └── models/           # SQLAlchemy ORM models
│       │
│       └── workers/
│           └── celery_app.py     # Celery app init — registers tasks from vigil-tasks
│
├── vigil-tasks/                  # Shared Celery task definitions (installed in both containers)
│   └── vigil_tasks/
│       ├── __init__.py
│       └── analysis.py           # Task signatures: run_inference(analysis_id)
│
└── ml-service/                   # Isolated ML worker — separate venv, separate container
    ├── Dockerfile
    ├── pyproject.toml            # MMAction2 + its dependencies
    └── worker/
        ├── celery_app.py         # Celery worker init — listens on `ml` queue only
        ├── config.py             # Model paths, device config, inference params
        ├── recognizer.py         # Model loader and wrapper (C3D / I3D via MMAction2)
        └── inference.py          # Inference pipeline (preprocess → forward → postprocess)
```

---

## Modules

### `auth`
Handles user registration, login, and token lifecycle. Issues JWT access and refresh tokens. Token issuance lives here; token verification lives in `security/`.

### `users`
Owns the `User` domain entity and profile management. Exposes `UserRepository` port used by `auth` and `security/`.

### `videos`
Manages video uploads and metadata. Streams uploads to MinIO, stores the MinIO path and metadata in Postgres. Exposes `VideoRepository` port consumed by the `analysis` module — the only cross-module dependency allowed.

### `analysis`
Triggered manually by the user with a `video_id`. Creates an `Analysis` record (`status: PENDING`), dispatches a `run_inference` Celery task via `vigil-tasks`, and returns immediately. The ML worker independently picks up the task, runs inference, and writes results back to Postgres. The main app reads results on poll. Optionally stores history for authenticated users.

---

## ML Layer

MMAction2 and its dependencies are highly version-sensitive and incompatible with the main application's dependency tree. For this reason the ML inference pipeline runs as a **separate Docker container** with its own isolated venv.

### vigil-tasks

`vigil-tasks` is a minimal shared Python package installed in **both** the main app container and the ML worker container. It contains only Celery task signatures — no inference logic, no MMAction2 imports.

```
vigil_tasks/analysis.py
  └── @celery.task(name="run_inference", queue="ml")
        def run_inference(analysis_id: str): ...
```

This is the only shared contract between the two containers. Neither side needs to know about the other's implementation.

### How it works at runtime

```
Main app container                Redis               ML worker container
  (vigil)                        (broker)              (ml-service)

  AnalysisService
    .trigger(analysis_id)
    → run_inference.delay()  ──────────────────>  Celery worker picks up task
                                                   → fetches video path from Postgres
                                                   → downloads from MinIO
                                                   → runs MMAction2 inference
                                                   → writes result to Postgres
                                                   → updates AnalysisStatus: COMPLETED
```

The ML worker listens **exclusively on the `ml` queue** via Celery task routing. The main app never imports anything from `ml-service/`.

### Swapping models

Replacing C3D with I3D or any other MMAction2-compatible model requires changes only inside `ml-service/worker/`. The task signature in `vigil-tasks` and the main application are untouched.

---

## Security

### Authentication
- Token issuance: `auth` module (`AuthService`)
- Token verification + current user extraction: `security/` (shared, no module dependency)
- Any router that needs the current user injects `get_current_user` from `security/dependencies.py`
- Frontend **never** parses the JWT — identity is always extracted server-side from the verified token

### JWT
- Access token: short-lived (15 min)
- Refresh token: long-lived (7 days), stored as `httpOnly` cookie
- Refresh Token Rotation: old token invalidated on each refresh
- Payload: `sub` (user_id), `exp`, `iat`, `jti`

### Passwords
- Hashed with **Argon2id** via `argon2-cffi`
- Hash stored in `password_hash` column, never plaintext

---

## Request Flows

### Video Upload
```
POST /videos/upload
  → FastAPI streams file to MinIO
  → Saves metadata + MinIO path to Postgres
  → Returns video_id, status: READY
```

### Trigger Analysis (manual)
```
POST /analyses
  body: { video_id }

  → Validates video ownership
  → Creates Analysis record (status: PENDING)
  → Dispatches Celery task with analysis_id
  → Returns analysis_id immediately (non-blocking)
```

### Celery Worker
```
Task receives analysis_id
  → Fetches video path via VideoRepository port
  → Downloads video from MinIO
  → Calls MLClassifier.predict(video_path)
  → Writes ClassificationResult to Postgres
  → Updates Analysis status: COMPLETED
```

### Poll Results
```
GET /analyses/{analysis_id}
  → Returns { status, result } — result populated when COMPLETED
```

### Analysis History (optional)
```
GET /analyses
  → Returns paginated list of past analyses for the authenticated user
```

---

## Workers

`src/vigil/workers/celery_app.py` initializes the Celery app for the **main container** and registers tasks imported from `vigil-tasks`. It does not contain any task logic.

`ml-service/worker/celery_app.py` initializes a **separate Celery worker** that listens only on the `ml` queue. All inference logic lives here. This worker is the only process that imports MMAction2.

Both workers share the same Redis broker and the same Postgres instance, but have completely separate dependency trees and Docker images.

---

## Inter-module & Inter-service Communication

```
analysis → videos      : via VideoRepository port (analysis/ports.py)
auth     → users       : via UserRepository port (users/ports.py)
any      → security    : via get_current_user dependency (security/dependencies.py)
vigil    → ml-service  : via Celery task queue (vigil-tasks package, Redis broker)
```

The `analysis` module no longer holds an `MLClassifier` port — inference is fully delegated to the ML worker via the task queue. The main app only dispatches `run_inference(analysis_id)` and later reads the result from Postgres when the worker writes it back.

This boundary means the ML service can be replaced, restarted, or scaled independently without touching the main application.