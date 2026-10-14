# Security, settings and Git rules

Inspect relevant files and root Git status before changes. The latest user instruction authorizes one root repository for frontend, backend and shared documents. No nested repositories or submodules. Do not commit, push, reset, rebase, force-push, change remotes, remove branches or destructively clean without authorization.

Never print/read secret values unnecessarily, include them in prompts/memory, or commit `.env` files. `.env.example` contains placeholders only; keep original private files unchanged and load them by path instead of copying secrets. Frontend settings are public. MongoDB credentials stay server-side; weather providers must require no API keys in the initial scope.

Validate shape, ranges and resource size before work. Do not accept arbitrary URLs or database operators. Use fixed provider hosts, bounded timeouts/retries, exact CORS origins and sanitized errors/logs. Follow [backend security](../../backend/docs/security.md); configuration is validated at startup and production must fail clearly if required settings are missing.

All additional tool installations, authentication, hook trust, tool updates that change the environment, AI routing and separate services require explicit approval under the [shared workflow](../../docs/ai-development-workflow.md). Prepare exact scope, writes, network/data access, verification and rollback first; install/test only one approved integration at a time. Never upload private source through an outside review or documentation provider without authorization. Ordinary focused, reversible work within the authorized task does not need repeated confirmation. Keep the private brief and derived screenshots out of public files.
