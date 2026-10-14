# Backend

FastAPI connectivity and request/error schema foundation with passing deterministic tests; no analysis, provider adapter, persistence repository, cache or climate engine exists. Read [instructions](AGENTS.md), [state](docs/state.md), [tasks](docs/tasks.md), [system design](docs/system.backend.md) and the [shared contract](../INTEGRATION_CONTRACT.md). The 85-concept pass is documentation-only; connectivity code was drafted before that scope change.

## Existing environment and commands

From `C:\Climate Hazard Trend Analyzer\backend`, uv uses [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock); dependencies were installed into local .venv on Python 3.14.2. No global package installation or package-manager replacement occurred.

```powershell
uv sync --frozen --cache-dir .uv-cache
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m compileall -q app
uv lock --check --offline --cache-dir .uv-cache
```

All four checks passed on 2026-10-14 (142 tests) on Python 3.14.2. The 80-test suite at that point also passed on Python 3.12.3 in a throwaway environment; 3.13 is untested. Tests are deterministic: a fixture blocks non-loopback network and real credential files, so they never contact Atlas or weather providers. Other declared Python versions and a clean checkout have not been exercised. A dependency advisory audit has not run. Starlette 1.8 warns that `TestClient` over `httpx` is deprecated; switching needs an approved dependency change.

## Atlas settings

[.env.example](.env.example) contains placeholders only. The local ignored .env holds `MONGODB_ENV_FILE` pointing to the existing user-owned private file, plus `MONGODB_DATABASE=climate_hazard_analyzer` and non-secret provider options. No URI/password was copied. Keep that external file private and unchanged; it is not part of the workspace.

Process environment overrides local .env. If MONGODB_URI is absent, only that key is read from MONGODB_ENV_FILE; unrelated file entries are ignored and interpolation is disabled. Alternatively inject MONGODB_URI directly through a server secret manager. Do not place it in frontend settings, terminal history or logs. Root/backend ignore rules exclude local environment and credential files. This directory belongs to the single root repository, which has no commits or remote yet.

The lifecycle uses one PyMongo async client per lifespan, driver timeouts plus a total `asyncio.timeout` per ping/close (MONGODB_TIMEOUT_MS), startup ping, and closure after success, failure or cancellation. No database schemas, collections or indexes were created. An earlier live Atlas ping **failed** with the redacted category `network_or_availability`. Rotate the previously exposed Atlas password before any new live attempt. [Troubleshooting](docs/database.md) separates syntax/encoding/auth/DNS/network checks without printing secrets or broadening network access.

## Conditional startup and health verification

The target exists, but startup/live readiness has **not** been verified because Atlas ping failed. After resolving connectivity and completing BE-009 tests, the intended local-only command is:

```powershell
uv run --frozen uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Then verify (commands not yet executed against a running server):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

Liveness is cheap and does not call storage/providers. Readiness pings storage and must expose only safe availability/error fields. Startup refuses an unavailable required DB. These routes are draft code, not evidence that the full API exists. No server or public listener was started.

## Weather providers and limits

Both public NASA POWER and Open-Meteo endpoints returned complete basic 1990–2020 samples without credentials at the test point. NASA is the configured preferred source; local non-commercial assessment settings enable Open-Meteo fallback. Default/example settings disable that fallback until usage eligibility is confirmed. See [provider policy/evidence](docs/data-pipeline.md) and [configuration](docs/security.md). No API-key setting or paid provider is supported.

Adapters for both providers exist and are tested; the fallback selector is still TODO. Real cache reuse and analysis require BE-005 / BE-007. Contract 0.2 (DOC-004) defines truthful source metadata for both providers; app/schemas.py enforces it.

Root instructions rely on the single-root layout ([DOC-002](../TASKS.md)). Never copy the private assessment or credentials into public deliverables.
