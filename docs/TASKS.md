# Vigil — Development Backlog

## Workflow

1. Pick tasks in order (Phase 1 → Phase 2 → ...)
2. Create a **separate branch** for each task: `feature/phase-1/task-1-project-setup`
3. Write **tests** alongside the code — never after
4. Open a **Pull Request** for review before merging to `main`
5. Never push secrets, `.env` files, or model checkpoints — EVER

---

## Phase 1: Foundation

### Task 1.1: Project Initialization
**Goal:** Set up the development environment and core configuration.

**Deliverables:**
- [x] `pyproject.toml` with all dependencies (FastAPI, SQLAlchemy, Alembic, pydantic-settings, redis, celery, minio, argon2-cffi, python-jose)
- [x] Configure `[tool.ruff]` for linting
- [x] `.env.example` with all required variables — no real values
- [x] `docker-compose.yml` with PostgreSQL, Redis, MinIO, main app, and ML worker services
- [x] `Dockerfile` for the main app container
- [x] `ml-service/Dockerfile` for the ML worker container (separate base image, separate venv)
- [x] `vigil-tasks/` package scaffolded with its own `pyproject.toml` — installed in both containers
- [x] `core/config.py` — `Settings(BaseSettings)` loading from `.env`
- [x] Verify: `docker-compose up` starts all services and `main.py` runs

**References:**
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Docker Compose](https://docs.docker.com/compose/)

---

### Task 1.2: Database Setup
**Goal:** SQLAlchemy 2.0 async engine + Alembic migrations configured and working.

**Deliverables:**
- [x] `database/session.py` — async engine + sessionmaker
- [x] `database/models/base.py` — `DeclarativeBase`
- [x] Alembic configured with async support (`alembic.ini`, `alembic/env.py`)
- [x] Verify: `alembic upgrade head` runs without errors on a clean DB

**Constraints:**
- Use `mapped_column()` syntax (SQLAlchemy 2.0)
- UUID primary keys throughout

**References:**
- [SQLAlchemy 2.0 async docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic async setup](https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic)

---

### Task 1.3: Redis & Celery Setup
**Goal:** Redis connection and Celery app initialized in the main container; ML worker container configured to listen on a dedicated queue.

**Deliverables:**
- [x] `database/redis/` — async Redis client (connection pool)
- [x] `workers/celery_app.py` — Celery app initialization in the main container, Redis as broker only (`task_ignore_result=True`)
- [x] `vigil-tasks/` — shared task definitions package installed in both containers
- [x] `ml-service/worker/celery_app.py` — Celery worker init in the ML container, configured to listen on the `ml` queue only
- [x] Celery task routing configured: `run_inference` tasks always route to the `ml` queue
- [x] Verify: a test task dispatched from FastAPI is picked up and executed by the ML worker container
- [ ] `ml-service/worker/db.py` — deferred to Task 4.2 (requires Video and Analysis models)
- [ ] `ml-service/worker/storage.py` — deferred to Task 4.2 (requires video upload path format)

**References:**
- [Celery with Redis](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html)
- [Celery task routing](https://docs.celeryq.dev/en/stable/userguide/routing.html)
- [FastAPI + Celery pattern](https://testdriven.io/blog/fastapi-and-celery/)

---

### Task 1.4: MinIO Setup
**Goal:** MinIO client configured and basic operations working.

**Deliverables:**
- [x] MinIO service in `docker-compose.yml` with a default bucket
- [x] `database/` — MinIO client wrapper (upload, download, delete, presigned URL)
- [x] Verify: upload a test file via the client and retrieve it successfully

**References:**
- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/API.html)

---

## Phase 2: Auth & Users

### Task 2.1: User Domain Layer
**Goal:** Define the User domain entity and its contracts.

**Deliverables:**
- [ ] `modules/users/domain/` — `User` entity, `UserId` value object, domain exceptions (`UserNotFoundError`, `UserAlreadyExistsError`)
- [ ] `modules/users/ports.py` — `UserRepository` ABC
- [ ] `database/models/user.py` — SQLAlchemy `UserModel` (id UUID, email, password_hash, created_at, is_active)
- [ ] First Alembic migration: `create_users_table`
- [ ] `modules/users/infrastructure/` — `UserRepository` implementation
- [ ] Unit tests: User entity creation, value object validation, domain exceptions

**Constraints:**
- Column: `password_hash`, never `password`
- Index on `email`

---

### Task 2.2: Password Hashing
**Goal:** Secure password storage with Argon2id.

**Deliverables:**
- [ ] `security/` — `PasswordHasher` class
- [ ] Methods: `hash(password: str) -> str`, `verify(password: str, hash: str) -> bool`
- [ ] Unit tests: hash is created, verify works, wrong password returns False, two hashes of same password differ

**Study:** Why is Argon2id preferred over bcrypt? What makes a function memory-hard?

**References:**
- [argon2-cffi docs](https://argon2-cffi.readthedocs.io/en/stable/)

---

### Task 2.3: JWT Token Service
**Goal:** Access + refresh token issuance and verification.

**Deliverables:**
- [ ] `security/token.py` — `TokenService`
  - `create_access_token(user_id) -> str` (15 min lifetime)
  - `create_refresh_token(user_id) -> str` (7 days)
  - `decode_token(token) -> TokenPayload`
- [ ] `security/dependencies.py` — `get_current_user` FastAPI dependency
- [ ] Unit tests: token creation, decoding, expired token raises error, tampered token raises error

**Constraints:**
- Secret key from `Settings`, never hardcoded
- Algorithm: HS256 minimum, EdDSA preferred
- Minimal payload: `sub` (user_id), `exp`, `iat`, `jti`

**References:**
- [python-jose docs](https://python-jose.readthedocs.io/en/latest/)
- [JWT best practices (RFC 8725)](https://datatracker.ietf.org/doc/html/rfc8725)

---

### Task 2.4: Auth Service & Endpoints
**Goal:** Registration, login, token refresh flow.

**Deliverables:**
- [ ] `modules/auth/application/` — `AuthService` (register, login, refresh, logout)
- [ ] `modules/auth/application/dto.py` — `RegisterDTO`, `LoginDTO`, `TokenPairDTO`
- [ ] `modules/auth/presentation/` — router with endpoints:
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`
- [ ] Unit tests: AuthService logic
- [ ] Integration tests: all four endpoints, including invalid credentials and duplicate registration

**Security requirements:**
- Refresh token in `httpOnly` cookie
- Refresh Token Rotation: old token invalidated on each refresh
- Return identical error message for "user not found" and "wrong password" (prevents user enumeration)

---

### Task 2.5: Users Endpoints
**Goal:** Authenticated user profile access.

**Deliverables:**
- [ ] `modules/users/application/` — `UserService`
- [ ] `modules/users/presentation/` — router:
  - `GET /api/v1/users/me`
  - `PATCH /api/v1/users/me`
- [ ] Integration tests: fetch own profile, update profile, unauthenticated request returns 401

---

## Phase 3: Videos

### Task 3.1: Video Domain Layer
**Goal:** Define the Video entity and storage contract.

**Deliverables:**
- [ ] `modules/videos/domain/` — `Video` entity, `VideoStatus` enum (`UPLOADED`, `READY`), domain exceptions
- [ ] `modules/videos/ports.py` — `VideoRepository` ABC
- [ ] `database/models/video.py` — SQLAlchemy `VideoModel` (id, owner_id FK, filename, minio_path, status, uploaded_at)
- [ ] Alembic migration: `create_videos_table`
- [ ] `modules/videos/infrastructure/` — `VideoRepository` implementation
- [ ] Unit tests: Video entity, status transitions, exceptions

---

### Task 3.2: Video Upload Endpoint
**Goal:** Single video upload streamed to MinIO.

**Deliverables:**
- [ ] `modules/videos/application/` — `VideoService` (upload, get_by_id, list)
- [ ] `modules/videos/presentation/` — router:
  - `POST /api/v1/videos/upload` — authenticated, streams to MinIO, saves metadata to Postgres
  - `GET /api/v1/videos` — list own videos
  - `GET /api/v1/videos/{video_id}` — get video metadata
- [ ] File type validation (accept: `.mp4`, `.avi`, `.mov`)
- [ ] Integration tests: upload, list, get, unauthenticated upload returns 401, invalid file type returns 422

**Constraints:**
- Owner check: users can only access their own videos
- Store MinIO object path in Postgres, not the raw file

---

### Task 3.3: Batch Upload (TBD)
**Goal:** Upload multiple videos in a single request.

**Status:** Postponed — design decision pending. Revisit after Task 3.2 is complete.

**Options to evaluate:**
- Single endpoint accepting multiple files (`List[UploadFile]`)
- Client-side loop calling the single upload endpoint per file
- Dedicated batch endpoint returning a list of `video_id`s

---

## Phase 4: Analysis

### Task 4.1: Analysis Domain Layer
**Goal:** Define the Analysis entity and ML contract.

**Deliverables:**
- [ ] `modules/analysis/domain/` — `Analysis` entity, `AnalysisStatus` enum (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`), `ClassificationResult` value object, domain exceptions
- [ ] `modules/analysis/ports.py` — `MLClassifier` ABC (`predict(video_path: str) -> ClassificationResult`), import `VideoRepository` from `modules/videos/ports.py`
- [ ] `database/models/analysis.py` — SQLAlchemy `AnalysisModel` (id, video_id FK, owner_id FK, status, result JSON, created_at, completed_at)
- [ ] Alembic migration: `create_analyses_table`
- [ ] Unit tests: Analysis entity, status transitions, ClassificationResult

---

### Task 4.2: ML Service Infrastructure + Classifier Implementation
**Goal:** Complete the ML worker's infrastructure clients and wire the MMAction2 inference pipeline.

**Deliverables:**
- [ ] `ml-service/worker/db.py` — sync psycopg2 client with two queries: fetch video minio_path by analysis_id, write result and update status
- [ ] `ml-service/worker/storage.py` — MinIO client for downloading video to a temp file
- [ ] `ml-service/worker/config.py` — model config (checkpoint path, mmaction2 config path, device, labels)
- [ ] `ml-service/worker/recognizer.py` — model loader and wrapper
- [ ] `ml-service/worker/inference.py` — inference pipeline (preprocess → forward pass → postprocess)
- [ ] Unit tests: mock inference for use in task tests
- [ ] Integration test: run inference on a short sample video, assert result shape is correct

**Constraints:**
- `db.py` uses sync `psycopg2` — no async in Celery tasks
- `storage.py` downloads to a temp file path, caller is responsible for cleanup
- Inference code never imports from `src/vigil/` — fully isolated

**References:**
- [MMAction2 inference guide](https://mmaction2.readthedocs.io/en/latest/user_guides/inference.html)
- [psycopg2 docs](https://www.psycopg.org/docs/)

---

### Task 4.3: Celery Analysis Task
**Goal:** Async inference dispatched through Celery, ML worker handles the full execution.

**Deliverables:**
- [ ] `vigil_tasks/analysis.py` — full task implementation:
  - Fetch video `minio_path` via `db.py`
  - Download video from MinIO via `storage.py` to a temp file
  - Run inference via `inference.py`
  - Write `ClassificationResult` to Postgres via `db.py`
  - Update `AnalysisStatus` to `COMPLETED` or `FAILED`
  - Clean up temp file
- [ ] Integration test: dispatch task, assert DB status transitions correctly

**Constraints:**
- Always clean up the temp file — use `try/finally`
- On any exception: set status to `FAILED`, log the error, do not crash the worker
- Never import from `src/vigil/` inside the task

---

### Task 4.4: Analysis Endpoints
**Goal:** REST API to trigger and poll analysis.

**Deliverables:**
- [ ] `modules/analysis/application/` — `AnalysisService` (trigger, get_by_id)
- [ ] `modules/analysis/presentation/` — router:
  - `POST /api/v1/analyses` — trigger analysis, body: `{ video_id }`
  - `GET /api/v1/analyses/{analysis_id}` — poll status and result
- [ ] Integration tests: trigger analysis, poll pending status, poll completed status, trigger on non-owned video returns 403

**Constraints:**
- Endpoint returns immediately after dispatching the Celery task
- Users can only trigger analysis on their own videos

---

## Phase 5: Polish

### Task 5.1: Analysis History
**Goal:** Allow users to view past analyses.

**Priority:** Low — implement only after Phase 4 is fully working.

**Deliverables:**
- [ ] `GET /api/v1/analyses` — paginated list of past analyses for the authenticated user
- [ ] Filter by status (optional query param)
- [ ] Integration tests: list own analyses, assert other users' analyses are not returned

---

### Task 5.2: Error Handling & Validation
**Goal:** Consistent error responses across all endpoints.

**Deliverables:**
- [ ] Global exception handler in `main.py` — maps domain exceptions to HTTP status codes
- [ ] Structured error response schema: `{ error: str, detail: str }`
- [ ] Validation errors (422) return field-level detail
- [ ] Tests: trigger each domain exception, assert correct HTTP status and response shape

---

### Task 5.3: Temp File & Worker Cleanup
**Goal:** Ensure no orphaned files or stale tasks accumulate.

**Deliverables:**
- [ ] Celery periodic task: mark analyses stuck in `PROCESSING` for over N minutes as `FAILED`
- [ ] Verify temp video files are always cleaned up after inference (covered by Task 4.3 `try/finally`)
- [ ] Tests: simulate stuck task, assert periodic cleanup fires correctly

---

## Development Guidelines

### Git
- Never push directly to `main` — PRs only
- Branch naming: `feature/phase-N/short-description`
- Commit messages: short, imperative mood (`Add video upload endpoint`)
- `.env` files and model checkpoints in `.gitignore` — always

### Code
- Type hints everywhere
- Docstrings on public methods — explain *why*, not *what*
- No magic numbers — use constants or enums
- Domain exceptions instead of generic `Exception`
- No raw SQL — ORM only

### Testing
- Tests written alongside code, not after
- Unit tests for domain layer — mandatory
- Integration tests for all endpoints — mandatory
- Use dependency injection to swap real infrastructure with mocks in unit tests
- No `print()` for debugging — use `logging` or `structlog`

### Security
- No secrets in code, ever
- No `eval()`, `exec()`, `os.system()`
- Input validation on every endpoint
- Owner checks on every resource endpoint
