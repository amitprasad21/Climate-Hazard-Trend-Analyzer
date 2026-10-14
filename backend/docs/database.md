# MongoDB model

Implemented in app/repositories/ (BE-005) and verified against a real local MongoDB 8.3.4; Atlas pending BE-009. Connectivity code exists separately from repository/schema design. A live Atlas ping using the supplied credentials file failed with network_or_availability; no successful connection, write permission or schema operation is verified. Keep an ordinary document model with explicit indexes; no generic query endpoint or user-supplied MongoDB expressions. BE-009 owns connection verification; BE-005 owns later explicitly scoped persistence implementation.

## daily_weather

Each document stores one normalized sampled-location day:

`source_key`, `requested_latitude`, `requested_longitude`, `resolved_latitude`, `resolved_longitude`, `model`, `timezone`, `variable`, `unit`, `date`, `tmax_c` (number or null), `quality` (valid/missing/invalid), `duplicate_dates` (0 or 1), `retrieved_at`, `expires_at`.

`source_key` identifies provider, model, canonical requested coordinates, timezone, variable, units and normalization version. Resolved coordinates are retained as metadata, not used to silently merge different requested locations whose elevation adjustment could differ. Box-level deduplication may reuse a proven identical provider series only after resolved identity/settings match.

Use ISO date strings consistently for indexed day ranges; use BSON UTC dates for timestamps. Validate allowed quality enums, finite numbers, ISO dates and field types at the adapter/schema boundary and add MongoDB collection validation during repository setup. Never store raw secrets, URLs with keys or arbitrary provider payloads.

Indexes: unique `(source_key, date)`; a TTL index on `expires_at` for physical cleanup. Reads must include expiry predicates because TTL removal is asynchronous. Unique keys make upserts retry-safe. Null/invalid days are explicit negative-cache records with a shorter expiry, so known missing records are not fetched on every request.

## analysis_cache

`cache_key` (SHA-256 canonical scientific inputs), `result` (validated response payload without request_id/current display label/cache.hit), `created_at`, `expires_at`, `source_fingerprint`.

Indexes: unique `cache_key`; TTL on `expires_at`. Validate payload contract/method version before serving. No separately exposed analysis ID is required. Cache key includes canonical region, period, baseline, percentile/method/run rules, regional sampling, quality policy, source/model/UTC/units and algorithm/normalization versions. Human-readable label is not a scientific cache input.

## Consistency and retention

Application result expiry is no later than the earliest contributing weather expiry and at most 24h. Source fingerprint is a digest of contributing source identities, data values and retrieval revisions. Repository tests must prove expired or method-incompatible results are never served.

Read/ingest in year chunks. A partially persisted batch is safe to retry via unique upserts; the service rereads and compares expected dates before computing. Do not mark a batch complete from the count of attempted writes. After refreshing weather, invalidate overlapping analysis records or ensure none can still be fresh under the expiry invariant. Administrative source correction must invalidate dependent caches explicitly.

Proposed valid-observation retention/freshness is 30 days; missing/invalid negative entries 1h; analyses up to 24h. These are operational assumptions, not provider guarantees. Re-fetch after expiry; avoid unbounded permanent storage in a public demo. Record disk/collection size before changing retention. Backups and migration strategy depend on the chosen deployment and remain unverified.

## Connection configuration and diagnostics

Existing `app/database.py` uses PyMongo AsyncMongoClient, created once per FastAPI lifespan, startup `admin.command("ping")`, pooled handles and awaited closure. The database name is `climate_hazard_analyzer`. Selecting a handle and pinging do not create collections. A request dependency reuses the lifespan client. Driver operation/selection/connect/socket/wait-queue timeouts default to 5000ms and apply per phase; ping and close are additionally capped by one `asyncio.timeout` of the same budget. Tests prove a stalled SRV lookup in the real installed driver is cancelled within that cap and that failed or cancelled startup closes the client. Live elapsed behavior against Atlas is unverified.

`MONGODB_URI` comes from process/local environment or the existing file named by `MONGODB_ENV_FILE`; the private file is not overwritten or copied. `.env` contains a path and non-secret options and is ignored. [.env.example](../.env.example) has placeholders only. [Backend README](../README.md) describes the current commands; [security](security.md) owns settings and secret handling.

| Safe symptom | Check privately | Prohibited shortcut |
|---|---|---|
| Missing/invalid configuration | MONGODB_URI presence, SRV syntax, URL-encoded username/password, valid database name; do not print value | Hardcoding or copying the secret |
| configuration_or_dns | DNS SRV resolution, reachable resolver, correct Atlas host, installed dnspython/PyMongo and loaded file | Disabling TLS or dumping URI/driver traces |
| authentication_or_permissions | Database user credentials/auth source and least-privilege roles; ping does not prove collection-write permission | Modifying credentials/roles without authorization |
| network_or_availability | Cluster availability, outbound network/firewall, certificate trust and precise Atlas IP access-list entry | Broadening to 0.0.0.0/0 |
| Startup fails / readiness 503 | Inspect safe reason and network prerequisites; unit tests distinguish app liveness from storage readiness | Starting an in-memory production database |

No specific cause of the live failure has been established beyond the safe network/availability category. DNS-versus-IP-allowlist-versus-cluster diagnosis remains open; do not claim a credential or permission problem from a generic timeout.
