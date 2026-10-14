# Backend operational runbook

Operational procedures, monitoring, troubleshooting, and deployment controls for Climate Hazard Trend Analyzer.

## 1. System architecture & process model

- **Process Model**: Single-worker FastAPI process (`uvicorn app.main:create_app --factory`).
- **Dependencies**:
  - Outbound HTTPS to NASA POWER (`power.larc.nasa.gov`) and Open-Meteo (`archive-api.open-meteo.com`, `geocoding-api.open-meteo.com`).
  - TLS-verified connection to MongoDB Atlas (or local loopback MongoDB in development).
- **In-Memory Guards**: Fixed-window rate limiters (5 analyses/min, 30 searches/min), max concurrency limiter (4 concurrent analyses), and per-key request coalescing locks.

## 2. Environment configuration checklist

Verify the following before starting the service:

| Variable | Recommended Production Value | Description |
|---|---|---|
| `MONGODB_URI` | `mongodb+srv://...` | MongoDB Atlas SRV URI with TLS enabled |
| `MONGODB_DATABASE` | `climate_hazard_analyzer` | Application database |
| `ALLOWED_ORIGINS` | `https://your-frontend.domain` | Comma-separated list of exact allowed frontend origins (no paths, no trailing slashes) |
| `WEATHER_PRIMARY_PROVIDER` | `nasa_power` | Primary daily historical reanalysis provider |
| `WEATHER_FALLBACK_PROVIDERS` | `open_meteo` | Secondary fallback provider |
| `WEATHER_FALLBACK_ENABLED` | `false` (or `true` if eligible) | Enables automatic whole-source fallback |
| `OPEN_METEO_NONCOMMERCIAL_USE` | `true` | Required if Open-Meteo is enabled |
| `ANALYSIS_RATE_PER_MINUTE` | `5` | Request quota per client IP |
| `SEARCH_RATE_PER_MINUTE` | `30` | Geocoding quota per client IP |
| `MAX_CONCURRENT_ANALYSES` | `4` | Max parallel analysis executions before returning HTTP 503 |
| `TRUSTED_PROXY_HOPS` | `1` (behind reverse proxy) | Number of reverse proxy hops to trust for client IP resolution |

## 3. Health checks and monitoring

### Liveness check
- **Endpoint**: `GET /api/v1/health`
- **Expected Status**: `200 OK`
- **Expected Body**: `{"status": "ok", "api_version": "v1"}`
- **Behavior**: Performs zero database or network I/O; used by load balancers / orchestrators to determine process liveness.

### Readiness check
- **Endpoint**: `GET /api/v1/health/ready`
- **Expected Status**: `200 OK`
- **Expected Body**: `{"status": "ok", "api_version": "v1", "database": "available"}`
- **Failure Status**: `503 Service Unavailable` with `{"error": {"code": "STORAGE_UNAVAILABLE", ...}}`
- **Behavior**: Executes an async `admin.command("ping")` with a strict 5000 ms deadline; does not leak credentials or connection strings on failure.

## 4. Performance benchmarking & telemetry

Run the benchmark script from the workspace root or against a running server:

```powershell
# In-process test against current settings:
python scripts/benchmark.py

# Against a running deployed instance:
python scripts/benchmark.py --base-url https://api.yourdomain.com --iterations 3
```

Target operational metrics:
- Liveness latency: < 5 ms
- Readiness latency: < 50 ms
- Warm cached analysis latency (p50): < 50 ms
- Cold analysis latency (30-year): < 10 s

## 5. Incident response & troubleshooting

### A. MongoDB Atlas Connection Failure (`STORAGE_UNAVAILABLE`)
- **Symptoms**: Readiness endpoint returns 503; analysis returns `STORAGE_UNAVAILABLE`.
- **Diagnostic Steps**:
  1. Inspect MongoDB Atlas network access list: ensure the server's public IP or VPC peering is authorized.
  2. Verify credentials in `MONGODB_URI`: check if the password expired or contains unencoded special characters.
  3. Verify DNS resolution: ensure the runner can resolve `_mongodb._tcp.<cluster>.mongodb.net`.
- **Remediation**: Update `MONGODB_URI` in process environment and restart service.

### B. Upstream Weather Provider Outage (`PROVIDER_ERROR` or `UPSTREAM_TIMEOUT`)
- **Symptoms**: Cold analysis requests take >10 s and fail with `UPSTREAM_TIMEOUT` or `PROVIDER_ERROR`.
- **Diagnostic Steps**:
  1. Check NASA POWER status page or curl `https://power.larc.nasa.gov/api/temporal/daily/point`.
  2. If NASA is degraded and `WEATHER_FALLBACK_ENABLED=true`, the selector will automatically try Open-Meteo.
- **Remediation**: If NASA POWER has extended maintenance, enable `WEATHER_FALLBACK_ENABLED=true` provided your deployment meets Open-Meteo terms.

### C. Rate Limiting Spikes (`RATE_LIMITED` / HTTP 429)
- **Symptoms**: Clients receive HTTP 429 with `Retry-After: 60`.
- **Diagnostic Steps**: Check if requests are coming from behind a corporate proxy or CDN where all users share an IP.
- **Remediation**: Configure `TRUSTED_PROXY_HOPS` correctly so the application inspects the actual client IP in `X-Forwarded-For`.

## 6. Graceful shutdown and rollback

- **Graceful Shutdown**: On receiving `SIGTERM` or `SIGINT`, FastAPI lifespan closes open database connections within the deadline.
- **Rollback Procedure**: If a deployment introduces a regression:
  1. Revert to the previous container image or Git commit hash.
  2. The MongoDB schema (`daily_weather` and `analysis_cache`) is backwards-compatible across minor versions.
  3. Purge `analysis_cache` collection if scientific methodology or contract schemas were modified:
     ```javascript
     db.analysis_cache.deleteMany({});
     ```
