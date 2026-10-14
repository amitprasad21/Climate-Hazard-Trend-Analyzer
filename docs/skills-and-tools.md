# Skills and tools registry

Original five-repository audit: 2026-10-13; AI-team compatibility refresh: 2026-10-14. Checked against official upstream documentation and local Codex help. **No new tool was installed, no hook trusted, and no external service started.** Reading instructions is distinct from installing/invoking a registered skill. Sources on `main` can change; recheck before executing an installer.

## Capability matrix

| Repository | Actual role | Project use | Installation required? / current state |
|---|---|---|---|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Engineering skills with native Codex plugin metadata | Specification, task breakdown, focused verification/review | Not required for this foundation; compatible CLI syntax verified, not installed |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Design skill, detector CLI, optional edit hooks/browser workflow | Product context, tokens, responsive/accessibility and state design | Not installed; manually read relevant guidance; defer engine/hooks until useful UI work |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Minimal-change skills plus lifecycle hooks in native plugin | Reuse, simpler boundaries, review affected callers and disclose limits | Not installed; principles applied manually; overlaps Addy review/simplification |
| [nexu-io/open-design](https://github.com/nexu-io/open-design) | Separate design workspace/desktop app, CLI and MCP/runtime adapters | Optional future prototype feedback only | Intentionally not installed; unnecessary for this dashboard foundation |
| [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute) | Long-running AI-provider gateway and CLI configuration tools | Optional development-workflow gateway only (user request 2026-10-14) | Not installed; awaits approval and provider accounts; excluded from application runtime. See [Claude Code audit](#claude-code-environment-audit--2026-10-14) |

## Local compatibility and categories

Codex CLI is 0.162.0-alpha.17.2; local `plugin marketplace add`, `plugin add`, `plugin list`, `plugin remove`, and `plugin marketplace upgrade` help exists. This is command-level evidence, not an end-to-end compatibility guarantee. Local plugin list/cache search found none of the five requested integrations. The remote marketplace listing failed; do not interpret that as absence from the remote catalog.

PDF/OpenAI Docs skills were available and used. Existing browser and code-review tooling can support later verification; not invoked against an application in this phase. PDF extraction/rendering, shell inventory, official web retrieval and documentation checks are development tools. Backend FastAPI/PyMongo/HTTPX dependencies are now locally installed and locked; React/charting remain future application dependencies. None of the five external repositories is a weather provider.

## Addy Agent Skills

Inspected [Codex setup](https://github.com/addyosmani/agent-skills/blob/main/docs/codex-setup.md), [manifest](https://github.com/addyosmani/agent-skills/blob/main/.codex-plugin/plugin.json), [specification skill](https://github.com/addyosmani/agent-skills/blob/main/skills/spec-driven-development/SKILL.md) and [planning skill](https://github.com/addyosmani/agent-skills/blob/main/skills/planning-and-task-breakdown/SKILL.md). Manifest reports 0.6.12. Upstream minimum is CLI 0.122; installed CLI exposes the documented syntax.

Official commands, **documented only, not run**; any working directory, modifies Codex marketplace/plugin registration and cache rather than app dependencies:

```powershell
codex plugin marketplace add addyosmani/agent-skills
codex plugin add agent-skills@agent-skills
```

Requires Git/network and Codex; no weather/AI credentials for reading skills. Verify local installed/enabled record with `codex plugin list --json`, then new-session skill discovery. Upstream documents `@spec-driven-development`; use the host's actual picker/name. Claude `/spec`, `/build` wrappers are not verified Codex commands. Single-skill installs may omit shared references; avoid assuming portability.

Check inventory before installation. Review a targeted `codex plugin marketplace upgrade agent-skills`, then available version/install behavior; never refresh all marketplaces casually. Remove with verified syntax `codex plugin remove agent-skills@agent-skills` only when requested. No app-code dependency or AGENTS copy is needed.

Applied manually: requirements before code and tasks with acceptance/evidence. User's combined foundation request takes precedence over generic stop-between-every-stage/auto-commit workflows. Never auto-run build-auto, ship, commits or hooks.

## Impeccable

Inspected [README](https://github.com/pbakaus/impeccable#installation), [actual Codex skill](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/SKILL.md), and its [init](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/init.md), [shape](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/shape.md), [new-work](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/new-work.md) and [operate](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/operate.md) references. Skill metadata reports 4.5.2. The current integration is one skill with subcommands, not an assumed older command pack.

Official project installer with documented options, **not executed**; run from the actual frontend repository when justified:

```powershell
npx impeccable install --providers=codex --scope=project
```

Requires npm/network for this installer; payload includes a Windows launcher and may download its engine under the user's `.impeccable` cache. It installs `.agents/skills/impeccable/` and project `.codex/hooks.json`; review every generated change. Detector use needs no LLM API key. Live mode needs a runnable UI/browser and may create local `.impeccable` state.

Verify files, new-session `/skills` or `$impeccable` discovery, and hook status in `/hooks`; do not auto-trust hooks. `npx impeccable update` refreshes an existing install; review scope/diff and renewed hook trust. `$impeccable hooks off` disables its detector through the supported workflow. For removal, use the installed version's documented procedure; otherwise inventory/backup and remove only its owned skill/hook entries, preserving other hooks. No uninstall command was verified.

Applied manually: PRODUCT/PRD separation, canonical visual-design authority, Operate dashboard brief and states. Launcher was unavailable; no context/detector/live command ran. The user's current monochrome palette in frontend/docs/design.md overrides generic palette advice; root DESIGN links to it. Do not run an installer, context engine download, live server or alternate-design tournament automatically.

## Ponytail

Inspected [SKILL.md](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md), [AGENTS.md](https://github.com/DietrichGebert/ponytail/blob/main/AGENTS.md), [INSTALL.md](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md) and [manifest](https://github.com/DietrichGebert/ponytail/blob/main/.codex-plugin/plugin.json). Manifest version 5.2.0 points to skills and two lifecycle hooks.

Official native commands, **not run**; any working directory, user Codex registration/cache changes:

```powershell
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

Requires Git/network and compatible Codex plugin/hook support; no provider key for instructions. Upstream calls for reviewing/trusting two hooks in `/hooks` and starting a new chat/app session. Verify installed/enabled listing and actual discovery. No Ponytail command is available in this current chat, so `/ponytail-review` was not invoked.

Check inventory to prevent duplicate skill/rules copies. Targeted marketplace refresh follows local help; review new hook definitions. Upstream uninstall now documents `codex plugin remove ponytail`; confirm the exact installed identity against local help before removal. Its INSTALL.md also describes optional residual state/statusline cleanup using the plugin-owned uninstall script before removing the plugin. Inspect those writes first, preserve other hooks/settings and never run it automatically. Mode off is not equivalent to uninstall; verify hook state too.

Applied: consolidated documents, native year inputs, no global store, no services/dependencies without need, retained safeguards and explicit unverified checks. Never replace this project's AGENTS with upstream AGENTS, automatically trust hooks, or delete code solely for brevity.

## OpenDesign

Inspected [README](https://github.com/nexu-io/open-design#quick-start), [agent adapters](https://github.com/nexu-io/open-design/blob/main/docs/agent-adapters.md), and [daemon data contract](https://github.com/nexu-io/open-design/blob/main/AGENTS.md#daemon-data-directory-contract). Upstream provides a Windows desktop distribution and Codex integration. It is not an installed skill here; PATH's Git `od.exe` is unrelated.

Optional setup after separate approval: install official desktop release, then use its Settings/MCP snippet with the real OpenDesign executable. Documented commands are `od mcp install codex --print` (preview), `od mcp install codex`, and `od mcp install codex --uninstall`. These are **not run or locally verified**. Use a neutral working directory and the verified executable path, outside the application runtime.

Requires separate app/daemon, storage and a supported agent/account or BYOK setup for generation. Installer can change agent MCP configuration and per-agent integration metadata; preview exact paths rather than guessing. Adapter-managed sessions can stage `.od-skills` in their working directory. Native Codex adapter uses app-server; prerelease preview behavior is explicitly conditional upstream, so this alpha CLI is not proof of every feature.

Verify MCP registration and a read-only project query after setup. Update via the chosen official distribution, preserving data; uninstall the integration before removing the app, retaining projects. Overlaps existing browser/manual design work, so no measurable need now. Never pipe remote install scripts to a shell, start its daemon or import private source automatically.

## OmniRoute

Inspected [README](https://github.com/diegosouzapw/OmniRoute), [security](https://github.com/diegosouzapw/OmniRoute/blob/main/SECURITY.md), [CLI integrations](https://github.com/diegosouzapw/OmniRoute/blob/main/docs/guides/CLI-INTEGRATIONS.md) and [Codex configuration](https://github.com/diegosouzapw/OmniRoute/blob/main/docs/guides/CODEX-CLI-CONFIGURATION.md). No routing need exists; evaluation stopped at documentation, without provider/account access.

Upstream documents `npm install -g omniroute` and a gateway commonly on port 20128. These are **not approved project instructions and were not run**. A future approved setup must choose a supported Windows release/runtime and minimum installation scope outside frontend/backend. No shell platform syntax has been translated and executed blindly.

Requires provider credentials/OAuth or configured accounts and persistent gateway storage; security docs describe JWT/API-key secrets and optional encryption that must be reviewed before startup. Configuring Codex can write profiles in the Codex home. `omniroute run codex` instead launches a child process with routing configuration; either route can transmit prompts/source to selected providers. It does not configure weather access.

If justified later: preview supported setup with `--dry-run`, inspect files/ports, obtain approval, verify loopback/authenticated routing with harmless input, and record precise rollback. Stop the gateway and restore/remove only its profile changes to disable; global npm uninstall is relevant only to a global install. Update through the chosen distribution after review. Never install, launch, open a public listener, switch providers, or send private code/secrets automatically.


## AI team capability audit — 2026-10-14

Rechecked Codex CLI 0.162.0-alpha.17.2, native plugin/MCP/review help, local plugin inventory, sanitized MCP names/enabled flags, common skill directories and current session tools. Node/npm, Git, Python and uv are available; Bun is absent. Root/frontend/backend Git status still reports no repository. No frontend package, scripts or runnable UI exists.

The local CLI inventory lists bundled Code Review/browser tooling. Its separate MCP entry for code-review is disabled, while this desktop session exposes a Code Review tool for PR CI diagnostics. These are different surfaces: neither proves a local review ran. No PR/repository exists to use that diagnostics tool here. Other installed document/browser tools do not supply Superpowers, Context7, Ponytail, Impeccable or gstack.

Plugin catalog search found Superpowers and Context7 with installed=false. No gstack result was returned; catalog search is not exhaustive. No requested team integration appears in local plugin/skill/MCP inventory. Official upstream support and local command availability are recorded below; **none has been installed or smoke-tested in this project**.

| Capability | Category / support evidence | Current use and decision |
|---|---|---|
| [Superpowers](https://github.com/obra/superpowers) | Planning/TDD skill plugin; official Codex App/CLI instructions and current manifest | Catalog-listed, not installed; manual planning now; overlaps Addy planning/review, so select one planner if later approved |
| [Context7](https://github.com/upstash/context7) | Documentation MCP/CLI plus optional skill/plugin; upstream Codex setup | Catalog-listed, not installed/connected; official web docs used now; no documentation query was sent through Context7 |
| Native Codex review / bundled Code Review | CLI review command; app plugin and PR checks tool | Installed/help-verified, project review execution unverified; manual file/caller review for this non-Git documentation change |
| Ponytail | Previously inspected minimal-change skill/plugin | Still not installed; skill and install/rules sources re-read, principles applied manually |
| Impeccable | Previously inspected UI skill/CLI/hooks | Still not installed; current skill/README re-read, canonical monochrome design retained |
| [gstack](https://github.com/garrytan/gstack) | Development skill suite, generated host integration and browser/build helpers; Codex tier experimental | Not installed; Bun missing, runtime support untested; use selective manual leadership/review passes |
| Existing browser tooling | Installed UI/browser automation | No application to inspect; all nine viewport checks remain NOT RUN |

Official [plugin](https://learn.chatgpt.com/docs/plugins) and [MCP](https://developers.openai.com/codex/mcp) documentation were read alongside local help. CLI listing produced PATH/temp permission and marketplace retrieval diagnostics; its empty remote-available list is not an exhaustive catalog. No configuration, provider, permission or credential was changed.

## Superpowers

Inspected current [README Codex sections](https://github.com/obra/superpowers#codex-app), [manifest](https://github.com/obra/superpowers/blob/main/.codex-plugin/plugin.json), [writing-plans](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) and [using-superpowers](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md). Manifest reports 7.0.0, skills directory and empty hooks. The older .codex/INSTALL.md and docs/README.codex.md URLs returned 404; do not follow a stale symlink tutorial.

Official installation route, **not executed**: Codex App Plugins → Superpowers → install; upstream CLI UI uses `/plugins`, searches Superpowers and selects Install Plugin. These are UI actions, not PowerShell commands. No working-directory-specific app install is needed. Prerequisites: supported Codex plugin surface, catalog/network access and explicit approval. Plugin registration/cache changes are user-level; inventory actual writes and manifest/permissions before accepting.

Verify the installed/enabled record, fresh-session skill discovery and one bounded planning exercise using the existing tracker. Read only the relevant skill; use its discovered name rather than assuming Claude slash wrappers. Record actual installed version and test output. No API key is needed merely to read instructions; do not start a visual companion or autonomous execution.

Use small verifiable plans and TDD where appropriate. Keep plans in existing local documents; user Git/approval/delegation rules override generic upstream commit, worktree or agent handoff suggestions. Avoid duplicate Addy/Superpowers workflow installs. For updates/removal, use the selected marketplace's supported controls after checking current help/installed ID, review changed permissions and repeat discovery/smoke checks. No Superpowers-specific update/uninstall command was locally executed.

## Context7

Inspected [Codex guide](https://github.com/upstash/context7/blob/master/docs/clients/codex.mdx), [README](https://github.com/upstash/context7) and [CLI lifecycle docs](https://github.com/upstash/context7/blob/master/docs/clients/cli.mdx). Node 18+ is documented for ctx7; local Node meets that floor. Upstream supports hosted MCP with a Codex plugin:

```powershell
codex plugin marketplace add upstash/context7
codex plugin add context7@context7-marketplace
```

These commands are **documented, not run**; any working directory, user Codex registration/cache and authenticated service access. Plugin setup opens OAuth; confirm account access and permissions explicitly before connecting. Start a fresh thread after installation. Do not combine plugin setup with the alternative `npx ctx7 setup --codex`: that can write Codex config and AGENTS instructions and authenticate/generate a key. Review exact files and keep credentials out of terminal commands, project docs and Git.

Verify registration/discovery, then resolve a public library and query documentation for one actual locked version; retain the official source and compatibility limits. Upstream MCP tools are named resolve-library-id and query-docs; they are not available in this session. Do not treat indexed latest documentation as proof for an older version.

Update only the chosen plugin/MCP/CLI route after approval; review version and repeat the same smoke check. For a native plugin, local removal syntax is `codex plugin remove context7@context7-marketplace`; remove only that registration. For ctx7-generated setup, upstream documents `npx ctx7 remove`; inspect target/mode first so unrelated instructions/config remain intact. Manual MCP removal uses the exact registered name with `codex mcp remove`; logout/revoke retained account credentials separately when requested. These are lifecycle instructions, not actions taken.

No Context7 SDK/server enters the application's dependencies. It overlaps available official web research; queries must exclude secrets/private source. No connection is needed for this documentation phase.

## Native code review

Local `codex review --help` confirms `--uncommitted`, `--base` and `--commit`. For an actual repository, run `codex review --uncommitted` from the affected frontend or backend root, with the existing authenticated Codex setup and permitted network. Review prompt/scope first and follow normal source-access policy; do not launch an outside AI-provider review. No extra review plugin is needed merely to read local files.

The bundled Code Review plugin is installed/enabled in CLI inventory; the desktop tool exposed here reads PR CI diagnostics, which is not a general local code-audit tool. Do not call it without a real selected PR. This phase uses direct document/caller checks because Git is absent. A temporary snapshot was created, but the sandbox did not preserve it across commands; no complete baseline diff/hash comparison is claimed. No native review execution or independent reviewer is claimed.

Verify future use on a bounded diff, inspect findings and test fixes. Native CLI updates follow the user's normal Codex installation channel; do not replace the host for this project. Stop invoking the CLI to discontinue it; any plugin removal requires a separate explicit request and the exact installed ID. No assumed `/code-review` command is added to AGENTS.

## gstack

Current [README](https://github.com/garrytan/gstack#other-ai-agents) labels Codex integration **experimental**, with advisory safety skills. It requires Git/Bun; Windows also requires Node. The documented tested Bun is 1.4.2+, with setup rejecting versions below 1.3.3. Bun is absent here. Outside reviews from Codex can use an authenticated Claude CLI; those are not authorized. Existing browser/manual review capabilities make installation unnecessary now.

Official Windows entry point is [setup.ps1](https://github.com/garrytan/gstack/blob/main/setup.ps1), which delegates to Git Bash. After a separately approved checkout/scope/prerequisite plan, run `.\setup.ps1 --host codex` from that tool checkout, outside application runtime. Do not run bare setup, host auto, team mode or upstream commit instructions. Codex capability names are generated with gstack prefixes; ask for the discovered skill instead of assuming Claude slash commands. Intended selection: product scope, architecture, design, QA, security and release-readiness review only when relevant.

Inspected [setup source](https://github.com/garrytan/gstack/blob/main/setup) and [host integration](https://github.com/garrytan/gstack/blob/main/docs/ADDING_A_HOST.md). Setup builds binaries/generates skills, may download browsers and optional security images, records installs/state and can write Codex skill/runtime directories. Project-local scope is supported by location; choose it only after inspecting the selected layout and global overlap. Inventory exact writes, network requests and scope before approval. Existing skill files may be copied on Windows; updates need setup again. Do not copy the entire digest into AGENTS or add a second runtime/database.

After installation, upstream `./setup --status` is a read-only inventory check; inspect the reported doctor path, discovery and one small non-shipping workflow. A successful setup does not prove browser or security helpers work. No local gstack command ran. Keep current model/provider settings; do not invoke cross-provider reviews, cookie/session imports or publication automatically.

Update the actual source checkout using the upstream procedure and regenerate only the selected host after approval. For removal, inspect [gstack-uninstall](https://github.com/garrytan/gstack/blob/main/bin/gstack-uninstall) before executing from the actual install: it can remove broad state and integrations, so confirm scope, preserve needed state and stop only owned processes. Its source documents interactive confirmation and keep-state; no dry-run option was found. Verify the installed version before any removal. Do not run its wildcard cleanup examples or force removal. Until that scoped procedure is approved, simply do not invoke its skills. Do not disable Windows security to launch unsigned helpers.

## Project workflow and evidence

Use [the canonical AI development workflow](ai-development-workflow.md) for roles, the ten-stage feature process, proportionate manual alternatives and approval gates. [AI_WORKFLOW](../AI_WORKFLOW.md) remains its entry point and CI plan. Read only needed skill instructions. The task trackers/design/methodology are the concrete outcome of this phase; no slash-command execution or external plugin installation is claimed.

DOC-008 owns conditional individual approved installation and capability smoke tests; none is selected now. Before future installs: obtain explicit approval for the prepared setup, recheck version/official source, inspect current local/global inventory and target Git status, understand writes, execute one operation at a time, review full diff, verify discovery, and record removal/rollback. Never bundle multiple installations, replace package managers, auto-approve hooks, edit secrets or add these tools to production dependencies.

## Claude Code environment audit — 2026-10-14

The development agent is now Claude Code 2.1.241 in the Claude desktop app on Windows 11 (Node 24.12.0, npm 10.2.5, uv 0.11.28, Python 3.14.2, Bun 1.4.2, Docker 28.4.0). Earlier Codex-specific findings above remain historical. Inspection was read-only; nothing was installed, configured or started.

**Superpowers.** Not installed. The already-registered `claude-plugins-official` marketplace lists `superpowers` pinned to commit `5bf4e78`. The official README gives `/plugin install superpowers@claude-plugins-official` (or the `obra/superpowers-marketplace` route). It adds skills (brainstorming, writing-plans, test-driven-development, systematic-debugging, verification-before-completion and others) and a **SessionStart hook** that injects its bootstrap into every session. Under the [shared workflow](ai-development-workflow.md), that hook needs explicit approval. Its brainstorming companion loads a remote logo; `SUPERPOWERS_DISABLE_TELEMETRY` disables it. The README gives no minimum Claude Code version and no uninstall command; `/plugin uninstall` is the generic route. BE-009 followed its method by hand: requirements, edge cases, plan, red tests first, then verification.

**OmniRoute.** Not installed: no binary, no global npm package, no `%APPDATA%/omniroute` data directory, and nothing listening on port 20128. npm reports `omniroute` 3.8.51 (MIT) with engine `>=22.22.2 <23 || >=24.0.0 <27`, which local Node 24.12.0 satisfies; GitHub's current release branch is v3.8.52. The official [Claude Code guide](https://github.com/diegosouzapw/OmniRoute/blob/main/docs/guides/CLAUDE-CODE-CONFIGURATION.md) supports Claude Code in two ways:
- `omniroute launch` health-checks the gateway, then starts `claude`.
- Manually set `ANTHROPIC_BASE_URL=http://localhost:20128` (no `/v1`; Claude Code appends `/v1/messages`) and `ANTHROPIC_AUTH_TOKEN` to an OmniRoute key from Dashboard → Endpoints.

`omniroute setup-claude --dry-run` previews per-model profiles under `~/.claude/profiles/<name>`, which are used through `CLAUDE_CONFIG_DIR`. It does not edit `~/.claude/settings.json` and never writes the token.

This applies to a separately launched `claude` CLI. The desktop app sets its own `ANTHROPIC_BASE_URL`, so the desktop session would not route through OmniRoute. The gateway is free and open source, but model access is not. Providers need the user's own accounts, keys or OAuth, each with its own quotas, terms and possible charges. OmniRoute's free-tier token figures are estimates across third-party tiers, not a grant, and a fresh install may have no eligible keyless route. Prompts and source code go to whichever provider the gateway selects.

Proposed setup, **not executed**, after explicit approval:
1. `npm install -g omniroute`, then start it with `omniroute` (dashboard and API on `localhost:20128`).
2. Add one provider through the dashboard, keeping credentials only in OmniRoute's encrypted store.
3. Create an OmniRoute key and supply it through an environment variable, never in a repository file.
4. Verify with `curl http://localhost:20128/v1/models` using that key, then send one harmless request to a model that is genuinely configured.
5. Launch with `omniroute launch` from a separate terminal.

To disable: stop the process, start `claude` without the gateway variables or profile, and remove any generated profile. To remove: `npm uninstall -g omniroute`, optionally deleting `%APPDATA%/omniroute`. MongoDB credentials, weather settings and application code never belong in OmniRoute.
