# Backend

FastAPI point-analysis backend: strict contract 0.3 schemas, NASA POWER and Open-Meteo adapters with whole-source fallback, MongoDB persistence and caching, the heatwave-v2 engine (Mann-Kendall trend test), place search, request guards, and 3×3 bounding box regional sampling (BE-006). Read [instructions](AGENTS.md), [state](docs/state.md), [tasks](docs/tasks.md), [system design](docs/system.backend.md) and the [shared contract](../INTEGRATION_CONTRACT.md).

## Environment and checks

From `C:\Climate Hazard Trend Analyzer\backend`, uv uses [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock); dependencies live in the local `.venv` (Python 3.14.2). No global packages were installed.

```powershell
uv sync --frozen --cache-dir .uv-cache
.\.venv\Scripts\python.exe -m pytest -m "not live_external"
$env:CLIMATE_TEST_MONGODB_URI = "mongodb://127.0.0.1:27017/?directConnection=true"; .\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m compileall -q app
uv lock --check --offline --cache-dir .uv-cache
```

All checks passed on 2026-10-14: 271 unit & integration tests (265 deterministic + 6 repository tests against real loopback MongoDB). Atlas connectivity and end-to-end analysis are verified live. OSV reports 0 advisories for the 26 locked packages.

## Running the API

The app is built by a factory, so importing `app.main` has no side effects. With Atlas, once the password has been rotated:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-proxy-headers
```

For local development against a loopback MongoDB, without editing `.env`:

```powershell
$env:MONGODB_URI = "mongodb://127.0.0.1:27017/?directConnection=true"
$env:MONGODB_LOCAL_DEVELOPMENT = "true"
$env:MONGODB_DATABASE = "climate_hazard_analyzer_dev"
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-proxy-headers
```

Startup pings MongoDB and creates the collections, validators and indexes. Routes:
- `GET /api/v1/health`
- `GET /api/v1/health/ready`
- `GET /api/v1/regions/search?q=…`
- `POST /api/v1/analyses/heatwaves`

Client identity for rate limits comes only from `TRUSTED_PROXY_HOPS`, which is why uvicorn runs with `--no-proxy-headers`. Verified 2026-10-14 against the local MongoDB: health, readiness, and a New Delhi 1995–2024 analysis (cold 7.0 s with live NASA POWER, repeat 7.7 ms from the cache).

## Settings and secrets

[.env.example](.env.example) contains placeholders only; [security](docs/security.md) lists every setting. The ignored local `.env` holds `MONGODB_ENV_FILE`, pointing to the user-owned Atlas credential file, plus non-secret options; no URI or password was copied. The process environment overrides `.env`. If `MONGODB_URI` is absent, only that key is read from `MONGODB_ENV_FILE`, and interpolation is disabled. Never put the URI in frontend settings, terminal history or logs.

`MONGODB_LOCAL_DEVELOPMENT=true` accepts only a loopback `mongodb://` URI without TLS; any other host still has to be a TLS-verified Atlas SRV URI. An earlier live Atlas ping failed (`network_or_availability`). Rotate the previously exposed Atlas password before any new live attempt (BE-009). [Troubleshooting](docs/database.md) separates syntax, encoding, auth, DNS and network checks without printing secrets.

## Weather providers

NASA POWER (MERRA-2, from 1981) is preferred. Open-Meteo ERA5 (from 1940) is a whole-dataset fallback used only when `WEATHER_FALLBACK_ENABLED` and `OPEN_METEO_NONCOMMERCIAL_USE` are true. The latter also enables place search, which uses the same free service. Sources are never mixed, and contract 0.2 reports each one truthfully. See the [provider policy](docs/data-pipeline.md). No API-key or paid provider is supported.

The backend is part of the single root repository ([DOC-002](../TASKS.md)). Never copy the private assessment or credentials into public deliverables.
