# PLAN.md — SDD Framework v2.0 Roadmap

> Spec-Driven Development Framework — a portable, agent-agnostic pipeline for governed software development with cron-driven automation and multi-agent coexistence.

**Status:** Planning · **Target tag:** `v2.0.0` · **License:** MIT

---

## 1. Vision

A spec-driven development framework that survives across sessions, agents, and operators.

The pipeline is the same regardless of which AI assistant runs each phase: a researcher agent today, a Claude Code session tomorrow, a Codex CLI batch job overnight. The state lives in the repo (not in any agent's memory), the gates are machine-verifiable (not prose), and a cron operator advances phases without human babysitting.

**Three load-bearing decisions:**

1. **Spec is the source of truth.** Any agent picking up the project reads the spec, not chat history.
2. **STATE.json is the GPS.** Machine-readable phase/branch/lock — cron parses it without an LLM call.
3. **AGENTS.md is the bridge.** A 60k+ project standard means no agent is excluded by default.

---

## 2. Non-Goals

- Replacing planning skills or spec tools that already work (this framework *orchestrates* them, doesn't reimplement them — see §3.8 for the OpenSpec and `agent-skills` integration).
- Becoming a full project management tool (no kanban, no time tracking, no team features).
- Locking users into a single AI vendor (every artifact must be readable by humans and by any agent; external engines are recommended defaults, never hard requirements).
- Solving deployment/CI/CD (those are downstream of `RELEASE`, not the framework's concern).

---

## 3. Architecture

### 3.1 Repository layout

```
sdd-framework/
├── README.md                    Public intro
├── PLAN.md                      This file (lives until v2.0 ships)
├── AGENTS.md                    Framework's own AGENTS.md (dogfooded)
├── LICENSE                      MIT
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md                 Append-only, semver
├── docs/                        Meta-docs about this repo (not the framework templates)
│   ├── IMPLEMENTATION-KICKOFF.md  Self-contained prompt to start a fresh impl session
│   └── history/                 PLAN.md archived here after v2.0.0 ships (see §9)
├── references/                  Long-form docs linked from short SKILL.md
│   ├── phase-research.md
│   ├── phase-discuss.md         (new in v2.0)
│   ├── phase-spec.md
│   ├── phase-plan.md
│   ├── phase-execute.md
│   ├── phase-verify.md
│   ├── phase-review.md
│   ├── phase-release.md         (split from SHIP)
│   ├── phase-archive.md         (split from SHIP)
│   ├── phase-observe.md         (optional, new in v2.0)
│   ├── portability-matrix.md
│   ├── integration-orchestrator.md
│   ├── integration-cron.md
│   ├── integration-openspec.md  (new in v2.0 — see §3.8)
│   ├── handoff-backends.md      (new in v2.0 — see §3.7)
│   └── borrowed/                (forked agent-skills, with attribution — see §3.8)
│       └── README.md            (fork-with-attribution policy)
├── templates/                   Copy-paste artifacts
│   ├── STATUS.md                Human-readable status
│   ├── STATE.json               Machine-readable state
│   ├── AGENTS.md                Project root template
│   ├── ADR.md                   Architecture Decision Record
│   ├── spec-delta.md            Per-change spec (manual fallback only — OpenSpec generates this natively)
│   ├── project.md               Source-of-truth spec (manual fallback only — `openspec init` generates this)
│   ├── cron-pipeline-manager.txt
│   ├── cron-single-project.txt
│   ├── handoff-schema.yaml      (new in v2.0 — see §3.7)
│   └── gates/
│       ├── research.yaml
│       ├── discuss.yaml
│       ├── spec.yaml
│       ├── plan.yaml
│       ├── execute.yaml
│       ├── verify.yaml
│       ├── review.yaml
│       ├── release.yaml
│       └── archive.yaml
├── scripts/                     Executable tooling (Python 3.10+, no extra deps by default)
│   ├── check-status.py          Watchdog — reads projects.yaml, returns JSON
│   ├── advance-pipeline.py      For cron --script preprocessing
│   ├── onboard.py               Bootstraps an existing project
│   ├── rollback.py              Moves a project back one phase
│   ├── acquire-lock.py          Multi-agent coordination
│   ├── handoff.py               Pluggable handoff backend (local | github | gitlab)
│   ├── migrate.py               v1.0 → v2.0 upgrade
│   └── bootstrap-portability.sh Symlinks / copies for cross-agent files
├── skill/                       Hermes Agent adapter (installable)
│   └── spec-driven-dev/
│       └── SKILL.md             Thin wrapper that links into ../../references/
├── examples/                    End-to-end runnable examples
│   ├── greenfield-cli-tool/
│   └── existing-project-onboarding/
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug.yml
    │   ├── feature.yml
    │   └── phase-improvement.yml
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/
        ├── lint.yml
        ├── test.yml
        └── validate-templates.yml
```

### 3.2 The 9-phase pipeline

Each phase is independently executable, gated by a YAML checklist that `scripts/advance-pipeline.py` can verify.

| # | Phase     | Input                  | Output                                              | Gate (excerpt)                                     |
|---|-----------|------------------------|-----------------------------------------------------|----------------------------------------------------|
| 1 | RESEARCH  | Problem statement      | `docs/research/YYYY-MM-DD-topic.md`                 | 2-3 approaches compared, links cited               |
| 2 | DISCUSS*  | Research               | `docs/discuss/YYYY-MM-DD-topic.md` Q&A              | Scope frozen, success criteria agreed              |
| 3 | SPEC      | Discussion (or Research) | `openspec/changes/<id>/{proposal,specs,design,tasks}.md` + ADRs | Functional + non-functional + acceptance criteria  |
| 4 | PLAN      | Spec (`tasks.md`)      | `.sdd/plans/YYYY-MM-DD-feature.md` (enriches `tasks.md` with TDD detail) | Tasks ≤5min, paths exact, copy-paste runnable      |
| 5 | EXECUTE   | Plan + `tasks.md`      | Code, semantic commits, passing tests               | Per-task two-stage review (spec → quality)         |
| 6 | VERIFY    | Code                   | `docs/verification/YYYY-MM-DD.json` (machine-readable) | All tests pass, lint clean, no regressions      |
| 7 | REVIEW    | Verified code          | `docs/review/YYYY-MM-DD.md`                         | No critical/important findings open                |
| 8 | RELEASE   | Reviewed code          | Tag, release notes, deploy artifact                 | Tag pushed, release notes published                |
| 9 | ARCHIVE   | Released code          | Change moved to `openspec/changes/archive/`, source-of-truth updated | Archive applied; `openspec/project.md` reflects new state |
| * | OBSERVE   | Released artifact      | `docs/observe/YYYY-MM-DD.md`                        | Window elapsed (24h/7d), no SEV-1 detected         |

`*` DISCUSS and OBSERVE are opt-in per `flavor`.

When `spec_engine = openspec` (the default — see §3.8), phases SPEC / EXECUTE / ARCHIVE invoke the OpenSpec CLI (`openspec propose` / `openspec apply` / `openspec archive`) and use its layout natively. When `spec_engine = manual`, the same artifacts are hand-written from `templates/spec-delta.md` + `templates/project.md`.

### 3.3 State separation

Two files. Different audiences. Different update cadences.

**`STATUS.md`** — narrative, human-first. Phase, next concrete step, blockers, full history table. Updated when phase moves.

**`STATE.json`** — frontmatter equivalent for machines. Cron parses with `jq`/Python and decides without an LLM.

```json
{
  "phase": "EXECUTE",
  "next_step": "Task 4 of 12 — implement message parser",
  "spec": "openspec/changes/0003-multi-channel/spec.md",
  "plan": ".sdd/plans/2026-05-11-multi-channel.md",
  "branch": "feat/multi-channel",
  "worktree": "/home/joao/projects/foo-multi-channel",
  "last_commit": "a1b2c3d",
  "last_agent": "claude-code",
  "last_update": "2026-05-11T14:32:00Z",
  "lock": { "agent": "codex-cli", "started_at": "2026-05-11T14:30:00Z", "ttl_minutes": 30 },
  "retry_count": 0,
  "last_error": null,
  "flavor": "software",
  "spec_engine": "openspec",
  "handoff_backend": "local"
}
```

### 3.4 Pipeline flavors

A `flavor` field selects which phases apply and which gates are enforced.

| Flavor       | Phases included                                     |
|--------------|-----------------------------------------------------|
| `software`   | Full 9-phase                                        |
| `automation` | Skip VERIFY (no test suite); REVIEW = manual sanity |
| `docs`       | RESEARCH → SPEC → EXECUTE → REVIEW → ARCHIVE        |
| `data`       | RESEARCH → SPEC → EXECUTE → VERIFY (data quality) → ARCHIVE |

Custom flavors live in `templates/gates/flavors/<name>/`.

### 3.5 Multi-agent coordination

- **Worktrees by default** when EXECUTE is parallelized (`scripts/onboard.py` enables this).
- **Lock with TTL** in `STATE.json` — any agent claiming work writes its name + start time + TTL. Stale locks (TTL expired) can be reclaimed.
- **Portability matrix** documents which file each agent reads natively, and which files require symlinks/copies.

### 3.6 Cron governance

Two patterns:

1. **Pipeline manager** — one cron job iterates over all projects in `~/.sdd/projects.yaml`, advances those whose gates pass, escalates those stalled > N days.
2. **Single project** — per-project cron tracks one repo, useful for high-cadence projects.

Both use `--script` (Python preprocessing) so the LLM only sees the diff that needs decisions, not raw STATUS.md content. Cron-aware retry: 3 failures → phase set to `BLOCKED`, non-silent notification dispatched.

### 3.7 Handoff and discussion layer

Phase state (§3.3) and handoff/discussion are distinct concerns. Mixing them couples a fast, offline-first machine artifact to a notification-heavy, internet-bound communication channel. The framework keeps them separate.

**Phase state** stays in `STATE.json` + `STATUS.md` — local, fast, offline-capable, vendor-neutral.

**Handoff and discussion** uses a pluggable backend declared in `STATE.json` via the `handoff_backend` field:

| Backend  | Default | Storage                                                                  | Best for                                                  |
|----------|---------|--------------------------------------------------------------------------|-----------------------------------------------------------|
| `local`  | ✅ yes  | `.sdd/handoffs/<id>.md`                                                  | Solo + offline. No external dependency.                   |
| `github` | opt-in  | GitHub Issues with `sdd:phase:*` and `sdd:waiting:*` labels              | Multi-agent + multi-machine + human collaboration         |
| `gitlab` | opt-in (post-v2.0) | GitLab Issues with parity schema                              | GitLab-hosted projects                                    |

**Cross-backend schema** (`templates/handoff-schema.yaml`):

```yaml
handoff:
  id: <uuid>
  from_agent: <name>
  to_agent: <name>
  phase: <RESEARCH | DISCUSS | SPEC | ...>
  context_link: <STATE.json path or commit ref>
  gate_passed: true | false
  decisions: [<short text per decision>]
  created_at: <ISO 8601>
  status: <pending | claimed | done | blocked>
```

**Deliberate tradeoff:** the `github` backend introduces a documented, opt-in vendor dependency. In exchange operators get (a) native atomic assignment without TTL locks during handoff, (b) threaded discussion that captures decision *why* (ADR.md captures only the *what*), and (c) free human notifications via `@`-mention. Operators who don't want any of that stay on `local` and pay zero cost — the principle from §2 (no vendor lock-in) is preserved by making `local` the default.

**Mention discipline (github backend only):**

- `@<human>` only when phase = `BLOCKED` or DISCUSS requires answers.
- Never `@<human>` for normal phase transitions — that is what STATUS.md history is for.
- Agents never `@<other agent>` — claim by writing the assignee field, not by mentioning. This is the lesson community operators learned the hard way (cascading agent-to-agent messages → "Noosphere" async patterns).

The adapter (`scripts/handoff.py`) exposes: `acquire`, `release`, `notify`, `list`, `migrate-backend`. Both `local` and `github` ship with v2.0; `gitlab` is parked.

### 3.8 Pluggable engines and prior art

The framework orchestrates; it does not reimplement tools that already work.

**Spec engine — `spec_engine` field in `STATE.json`:**

| Engine     | Default | Owns                                                                                                | Phases it drives                       |
|------------|---------|-----------------------------------------------------------------------------------------------------|----------------------------------------|
| `openspec` | ✅ yes  | `openspec/` tree (`changes/<id>/{proposal,specs,design,tasks}.md`, `changes/archive/`, `project.md`) | SPEC, the apply step of EXECUTE, ARCHIVE |
| `manual`   | opt-in  | Plain markdown via `templates/spec-delta.md` + `templates/project.md`                                | same, hand-written                     |

When `spec_engine = openspec`, the framework calls the [OpenSpec](https://github.com/Fission-AI/OpenSpec) CLI (`openspec init`, `openspec propose`, `openspec apply`, `openspec archive`) and reads/writes its layout natively. The framework **never patches OpenSpec internals** — if we ever need to diverge, that is a separate named fork, not a monkey-patch. OpenSpec is MIT-licensed and self-hostable, so this is a recommended-default dependency, not a vendor lock-in.

When `spec_engine = manual`, the framework uses its own thin markdown templates for the same artifacts — keeping the no-lock-in promise (§2) intact for operators who don't want the CLI.

**Technique guidance — `references/borrowed/`:**

Per-phase engineering technique (how to write a good spec, how to break down a plan, how to debug, how to ship) is imported from [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) (MIT) into `references/borrowed/<name>.md`. Each borrowed file leads with an attribution line (`Adapted from addyosmani/agent-skills @ <commit>, MIT`) and links back to the phase it serves. We **fork rather than link** so our docs don't break on upstream changes; the limit is ≤ 8 borrowed files to avoid becoming an unmaintained mirror. Policy lives in `references/borrowed/README.md`.

**What the framework still owns (not delegated):**

- The 9-phase pipeline shape and the gates (§3.2, §3.4).
- `STATE.json` + `STATUS.md` — phase state (§3.3).
- `AGENTS.md` universal bridge + portability matrix (§3.5).
- Cron governance + `--script` preprocessing (§3.6).
- Multi-agent locks (§3.5) and the handoff/discussion layer (§3.7).
- Migration tooling (§4) and the Hermes skill adapter.

---

## 4. Migration from v1.0

`scripts/migrate.py` performs an idempotent upgrade:

1. Detect v1.0 marker (`openspec/project.md` exists, no `STATE.json`).
2. Generate `STATE.json` from current STATUS.md (parse the `Fase atual:` line).
3. Add `flavor: software` default; set `spec_engine` to `openspec` if an `openspec/` tree exists, else `manual`; set `handoff_backend: local`.
4. Move `.hermes/plans/` → `.sdd/plans/` (symlink old location for back-compat).
5. Stamp `MIGRATION.md` with timestamp and origin version.

Migration is a no-op if `STATE.json` already exists.

---

## 5. Roadmap (Must / Should / Nice)

### 5.1 Must Have — required for v2.0.0 tag

| ID | Item | Owner | Acceptance |
|----|------|-------|------------|
| M1 | Extract framework-owned templates to files (STATUS, STATE, AGENTS, ADR, gates) — `spec-delta.md` + `project.md` only as `manual`-engine fallback | — | Files exist, are valid, and pass `scripts/validate-templates.py` |
| M2 | Implement `scripts/check-status.py` | — | Reads `~/.sdd/projects.yaml`, emits well-formed JSON, has unit tests |
| M3 | STATE.json schema + validator (includes `spec_engine` and `handoff_backend` enums) | — | `references/state-schema.json` + JSON Schema validation in CI |
| M4 | Document artifact ownership: OpenSpec owns `openspec/`, framework owns `.sdd/` + STATE/STATUS, orchestrator owns `.agent/` | — | `references/portability-matrix.md` with diagram, no overlap unresolved |
| M5 | Cron `--script` pattern documented and exemplified | — | `templates/cron-*.txt` work end-to-end against an example project |
| M6 | Gates as YAML, machine-verifiable | — | `templates/gates/*.yaml` validated; `scripts/advance-pipeline.py` consumes them |
| M7 | Terminology alignment with cron tooling | — | `references/integration-cron.md` cross-checked against current Hermes `cronjob` tool docs |
| M8 | README, CONTRIBUTING, SECURITY, AGENTS.md (dogfooded) | — | All present at root, follow Hermes community conventions |
| M9 | Hermes skill adapter (`skill/spec-driven-dev/SKILL.md`) | — | Skill loads in Hermes, points users at framework docs |
| M10 | Adopt OpenSpec as default SPEC/APPLY/ARCHIVE engine (§3.8); `spec_engine: openspec \| manual` | — | Framework calls `openspec` CLI for the relevant phases; `manual` fallback works; `references/integration-openspec.md` documents the contract; never patches OpenSpec internals |
| M11 | Map the 9 phases → OpenSpec command surface | — | `references/integration-openspec.md` includes a phase-to-command table; where a phase has no OpenSpec equivalent, the reason is stated |
| M12 | Pluggable handoff/discussion backend (`local` default + `github` opt-in) | — | `scripts/handoff.py` ships both adapters; `templates/handoff-schema.yaml` validated; `references/handoff-backends.md` documents the tradeoff and mention discipline; STATE.json schema (M3) extends with `handoff_backend` enum |

### 5.2 Should Have — strongly preferred for v2.0.0

| ID | Item | Acceptance |
|----|------|------------|
| S1 | Add DISCUSS phase (opt-in) | Phase doc + gate YAML + template question prompts |
| S2 | VERIFY via `execute_code` (deterministic) | `templates/verify-runner.py` runs pytest/eslint/etc, returns JSON |
| S3 | `scripts/onboard.py` for existing projects | Detects stack, generates STATUS/STATE/AGENTS, declares current phase |
| S4 | Worktree-by-default in EXECUTE when parallelism > 1 | `references/phase-execute.md` + `scripts/spawn-worktree.sh` |
| S5 | Multi-agent lock with TTL | `scripts/acquire-lock.py` + STATE.json schema field + tests |
| S6 | Cron retry + non-silent failure notification | Documented pattern + example with `[SILENT]` toggle |
| S7 | One reference doc per phase (under `references/`) | 9 files, each ≤120 lines |
| S8 | Greenfield example (`examples/greenfield-cli-tool/`) | Runnable end-to-end demo |
| S9 | Import 5–7 `agent-skills` as `references/borrowed/<name>.md` | Attribution line + back-link per file; ≤8 files; `references/borrowed/README.md` policy in place; candidates: `context-engineering`, `planning-and-task-breakdown`, `incremental-implementation`, `debugging-and-error-recovery`, `code-review-and-quality`, `shipping-and-launch` |

### 5.3 Nice to Have — post-v2.0.0 candidates

| ID | Item |
|----|------|
| N1 | Pipeline flavors: `automation`, `docs`, `data` |
| N2 | `.context/` two-layer context model (always vs on-demand) |
| N3 | OBSERVE phase post-RELEASE |
| N4 | `scripts/migrate.py` v1.0 → v2.0 |
| N5 | `scripts/bootstrap-portability.sh` with platform detection |
| N6 | RELEASE / ARCHIVE split into truly separate phases |
| N7 | Adapters for Codex CLI, Cursor, Aider beyond Hermes |
| N8 | VS Code extension that surfaces STATUS/STATE in the sidebar |
| N9 | `gitlab` handoff backend (parity with `github`); case-by-case Forgejo / Gitea / Codeberg |

---

## 6. Acceptance criteria for v2.0.0 tag

- All Must-Have items shipped.
- ≥ 6 of 9 Should-Have items shipped.
- Greenfield example runs from `RESEARCH` to `ARCHIVE` driven only by cron + skill adapter.
- Greenfield example uses the `openspec` engine for SPEC/APPLY/ARCHIVE; a test or second variant covers `spec_engine = manual`.
- Greenfield example demonstrates **both** handoff backends (`local` and `github`) end-to-end.
- Migration script tested against ≥ 1 real v1.0 project.
- Public docs (README + every `references/` file) reviewed by at least one external contributor.
- CI green: lint, template validation, JSON schema, example smoke test.

---

## 7. Out-of-scope for v2.0 (parking lot)

- IDE integrations beyond what AGENTS.md already enables.
- Web UI / dashboard.
- Hosted cron service.
- Built-in LLM calls (the framework orchestrates agents, doesn't call models directly).
- Marketplace for community templates/flavors.

These may move to v2.1+ if traction justifies.

---

## 8. Open questions

1. **Plan file location** — `.sdd/plans/` (proposed) vs reusing `.hermes/plans/` for Hermes users. Lean toward `.sdd/` for portability; provide symlink helper.
2. ~~**OpenSpec compatibility**~~ — **RESOLVED (§3.8):** adopt OpenSpec's `openspec/` layout verbatim as the default `spec_engine`; provide a `manual` fallback so the framework works without the CLI. Validate the exact layout against the pinned OpenSpec version during M10/M11.
3. **Lock semantics** — advisory only (any agent can override stale lock) vs enforced (require explicit release). Lean advisory.
4. **DISCUSS without humans** — when running fully autonomous via cron, who answers DISCUSS questions? With the `github` handoff backend (M12) one option is `@`-mention the operator on a DISCUSS issue and pause until they reply; with the `local` backend a sub-agent flavor drafts answers for human review. Pick once an example exists.

---

## 9. How this plan evolves

- This file lives at the repo root **until v2.0.0 ships**.
- After v2.0.0 tag: archive to `docs/history/PLAN-v2.md` and replace with `ROADMAP.md` (forward-looking, non-versioned).
- Each Must/Should item has a tracking issue. PRs link to the issue ID.
- Change to scope (add/remove a Must) requires a PR to this file with rationale.
