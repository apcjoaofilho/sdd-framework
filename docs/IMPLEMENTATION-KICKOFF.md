# Implementation Kickoff — SDD Framework v2.0

> **Purpose:** a self-contained prompt to start implementation in a fresh AI session
> (Claude Code, Hermes, Codex, etc.) that has **no prior chat history**. Paste the
> block below as the first message of that session.
>
> **Lifespan:** this file is relevant until the foundation issues (M3, M1, M6) are
> merged. After that, update it for the next batch or delete it — `PLAN.md` and the
> GitHub issues remain the authoritative source.

---

## How to use

1. Open a fresh session with the working directory at the repo root
   (`~/projects/sdd-framework` on the maintainer's machine, or wherever you cloned it).
2. Paste everything inside the fenced block below.
3. Let the session read the listed files, then implement PR 1 (M3) first.

---

## The prompt

```
# Task: Implement the SDD Framework foundation (issues M3, M1, M6)

## Context

You're working on **SDD Framework** — a portable, agent-agnostic spec-driven
development pipeline. Repo: https://github.com/apcjoaofilho/sdd-framework
Local clone: the current working directory should be the repo root, on git `main`.
If it isn't, stop and ask.

Status: planning is **complete**. Commits on `main` so far:
- scaffold (READMEs, AGENTS.md, LICENSE, .github/, empty dirs)
- PLAN.md with the full v2.0 roadmap + handoff layer (§3.7)
- OpenSpec adoption (§3.8) + references/borrowed/ policy
- this docs/IMPLEMENTATION-KICKOFF.md

There are open issues across 3 milestones (Must Have v2.0, Should Have v2.0,
Nice to Have). Nothing is implemented yet — `references/`, `templates/`,
`scripts/` contain only README stubs.

## Read these first (in order)

1. `PLAN.md` — the authoritative roadmap. §3 is the architecture. §5.1 lists
   Must-Haves. Pay special attention to §3.2 (9-phase pipeline), §3.3 (STATE.json
   / STATUS.md split), §3.7 (handoff layer), §3.8 (pluggable spec engine).
2. `AGENTS.md` — conventions for this repo (Python 3.10+, no third-party runtime
   deps, ruff, pytest, semantic commits, English in artifacts, no emoji, TDD for
   scripts).
3. `CONTRIBUTING.md` — branch naming, what needs tests, PR checklist.
4. `references/README.md`, `templates/README.md`, `scripts/README.md` — planned
   file inventories.
5. The three GitHub issues you'll implement (use `gh issue view <N>`):
   - **M3** = issue #3 — STATE.json schema + JSON Schema validator
   - **M1** = issue #1 — extract framework-owned templates to files
   - **M6** = issue #6 — gates as YAML, machine-verifiable

## What to build, in dependency order

These three are the foundation; M2/M5/M10/M12 all depend on them. Do them as
**separate PRs**, each branched from `main`, each linking its issue.

### PR 1 — M3 (issue #3): STATE.json schema
- Create `references/state-schema.json` (JSON Schema, draft 2020-12) covering
  every field in PLAN.md §3.3: `phase`, `next_step`, `spec`, `plan`, `branch`,
  `worktree`, `last_commit`, `last_agent`, `last_update`, `lock` (object with
  `agent`/`started_at`/`ttl_minutes`), `retry_count`, `last_error`, `flavor`
  (enum: software|automation|docs|data), `spec_engine` (enum: openspec|manual),
  `handoff_backend` (enum: local|github|gitlab).
- Create `pyproject.toml` (this repo has none yet — AGENTS.md says it lands with
  M1, but M3 needs it too; create it here, minimal: project metadata, `[dev]`
  extra with pytest/ruff/jsonschema, ruff config).
- Create `scripts/validate-state.py` — validates a STATE.json against the schema;
  `--format json|tty`; exit codes per `scripts/README.md` conventions.
- Tests: `tests/scripts/test_validate_state.py` — valid example passes, each
  bad-field variant rejects.
- Update `references/README.md` if needed; add a `## [Unreleased]` CHANGELOG entry.

### PR 2 — M1 (issue #1): framework-owned templates
- Create under `templates/`: `STATUS.md`, `STATE.json` (must validate against the
  M3 schema), `AGENTS.md` (project-root template), `ADR.md`. Also `spec-delta.md`
  and `project.md` but clearly labelled "manual engine fallback only — OpenSpec
  generates these natively when spec_engine=openspec". Also `cron-pipeline-manager.txt`
  and `cron-single-project.txt` (can be skeletal — M5 fills them).
- Each template starts with a header comment listing its placeholders.
- Create `scripts/validate-templates.py` — checks every file in `templates/`
  exists, parses, and (for STATE.json) validates against the schema.
- Tests: `tests/templates/test_templates.py`.
- Coordinate with M12 on `templates/handoff-schema.yaml` — you may stub it now or
  leave it for the M12 PR; note the decision in the PR description.
- CHANGELOG entry.

### PR 3 — M6 (issue #6): gates as YAML
- Define the gate-YAML schema (see the draft in `templates/gates/README.md`).
  Create `references/gate-schema.json` or document it inline — your call, but it
  must be machine-validatable.
- Create `templates/gates/{research,discuss,spec,plan,execute,verify,review,release,archive}.yaml`
  — one per phase, each with `phase`, `description`, `required[]`, `optional[]`
  where each check has `id`, `description`, `check.type` (one of `file_exists`,
  `file_contains`, `command_exit_zero`, `json_path_truthy`), `check.args`.
- Implement gate evaluation in a new module the future `scripts/advance-pipeline.py`
  (M5) will import — put it in `scripts/gates.py` with the four check types.
- Tests: `tests/scripts/test_gates.py` covering each check type + a passing/failing
  gate end-to-end.
- CHANGELOG entry.

## Hard constraints

- **Don't extend scope.** New phases, templates, scripts, or flavors require a PR
  to `PLAN.md` first. If you discover something missing, note it in the PR and/or
  open an issue — don't silently add it.
- **Don't reimplement OpenSpec.** The `openspec` CLI is the default spec engine
  (PLAN.md §3.8). We never patch its internals. The `manual` engine is just thin
  markdown templates.
- **Nothing Hermes-specific outside `skill/`.** `references/`, `templates/`,
  `scripts/` must work without Hermes installed.
- **Tests ship in the same PR** as the code they cover (repo convention).
- **No third-party runtime deps** in `scripts/` by default — `jsonschema` is a
  dev/CI dep, invoked from CI, not imported at runtime by the consumer-facing
  scripts (or if it must be, make it optional and documented).
- Semantic commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`), squash-merge,
  PR body links the issue (`Closes #N`), English only in committed artifacts,
  no emoji.

## Workflow per PR

1. `git checkout main && git pull`
2. `git checkout -b feat/<slug>`  (e.g. `feat/state-schema`)
3. Implement + tests.
4. `ruff check .` and `pytest` green.
5. Commit (semantic message), push, `gh pr create` with `Closes #N` in the body
   and the PR checklist from `.github/PULL_REQUEST_TEMPLATE.md` filled in.
6. Report the PR URL.

Start with PR 1 (M3). Confirm the plan with me before opening the PR if anything
in the issues conflicts with what's written here.
```

---

## Alternatives the maintainer may choose before running this

- **Direct-to-`main` instead of PRs.** Replace the "Workflow per PR" section with
  "commit directly to `main`, one semantic commit per issue". Use this for solo,
  fast iteration; switch to PRs once there are external contributors.
- **Narrower first session.** Cut the prompt down to **M3 only**. It's the hardest
  prerequisite and closes quickly; M1 and M6 then build on a settled schema.
- **Different agent.** The prompt is agent-neutral. For Hermes specifically, note
  that cron sessions have zero chat history — which is exactly why this prompt is
  written to be fully self-contained.
