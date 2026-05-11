# SDD Framework

> **Spec-Driven Development** — a portable, agent-agnostic pipeline for governed software development with cron-driven automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Planning](https://img.shields.io/badge/status-planning-orange.svg)](PLAN.md)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-supported-brightgreen.svg)](AGENTS.md)

SDD turns ad-hoc AI-assisted coding into a repeatable pipeline. Specs survive sessions, state lives in the repo, gates are machine-verifiable, and a cron operator advances phases without you babysitting it.

The same project can be picked up by Hermes today, Claude Code tomorrow, and Codex CLI overnight — none of them needs to know the others exist.

---

## Why

Every AI coding agent eventually hits the same walls:

- **Context dies between sessions.** The agent forgets what was decided, why, and where you stopped.
- **Multi-agent setups conflict.** Two agents in the same checkout overwrite each other.
- **Project state is invisible.** Was the spec done? Did review pass? Where do I resume?
- **Cron-driven work is fragile.** Cron sessions have zero history; a vague prompt is a broken job.

SDD answers all four with a small set of conventions: a 9-phase pipeline, a `STATE.json` that any tool can parse, an `AGENTS.md` any agent can read, and explicit gates between phases.

---

## How it works

```
RESEARCH → DISCUSS → SPEC → PLAN → EXECUTE → VERIFY → REVIEW → RELEASE → ARCHIVE
                                                                       ↘ OBSERVE (optional)
```

Each phase has:

- **An input** (what it expects).
- **An output** (a file committed to the repo).
- **A gate** (a YAML checklist a script can verify).

The pipeline is driven by:

- **`STATUS.md`** — narrative, human-first.
- **`STATE.json`** — machine-readable; cron parses it without an LLM.
- **`AGENTS.md`** — the bridge that makes any agent productive on the project.

A cron job iterates over your projects, advances those whose gates pass, escalates those that stall.

---

## Status

**Planning.** v2.0.0 is the first tagged release. See [PLAN.md](PLAN.md) for the roadmap and acceptance criteria.

A v1.0 of this framework existed as a Hermes Agent skill (`spec-driven-dev`). This repo absorbs the lessons from that prototype, splits it into a portable framework + thin Hermes adapter, and adds the missing pieces (STATE.json, gates as YAML, multi-agent locks, migration tooling).

---

## Quick taste — the pipeline applied to a tiny project

```bash
# Onboard an existing project (planned, not yet implemented)
python scripts/onboard.py /path/to/your/project --flavor software

# Look at where it is
python scripts/check-status.py /path/to/your/project

# Let the cron operator drive
hermes cronjob add "every 6h" \
  --script scripts/advance-pipeline.py \
  --name "sdd-pipeline-manager"
```

When v2.0 is shipped, the [`examples/`](examples/) directory will contain end-to-end runnable demos.

---

## For different audiences

- **Hermes Agent users** — install [`skill/spec-driven-dev/`](skill/spec-driven-dev/) once v2.0 ships. The skill is a thin wrapper around the framework; all logic lives in the framework.
- **Claude Code / Codex / Cursor / Aider users** — the `AGENTS.md` template at the project root is enough; templates and scripts work standalone.
- **Operators running multiple AI-assisted projects** — the cron governance pattern is for you. One job manages many projects.

---

## Repository layout

See [PLAN.md §3.1](PLAN.md#31-repository-layout) for the full inventory. The shape:

```
sdd-framework/
├── references/   long-form docs, one per phase + integration guides
├── templates/    copy-paste artifacts (STATUS, STATE, AGENTS, gates, cron prompts)
├── scripts/      Python tooling (check-status, onboard, rollback, migrate)
├── skill/        Hermes Agent adapter
├── examples/     end-to-end runnable demos
└── PLAN.md       v2.0 roadmap (this lives here until v2.0 ships)
```

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for the development setup, commit style, and how to propose a new phase, template, or flavor.

For security issues, see [SECURITY.md](SECURITY.md).

---

## Inspiration

SDD stands on the shoulders of:

- **[OpenSpec](https://github.com/Fission-AI/OpenSpec)** — spec-as-source-of-truth, delta specs, archived specs.
- **[GSD (Get Shit Done)](https://github.com/gsd-build/get-shit-done)** — explicit phases, `.planning/` state, cross-AI runtime.
- **[AGENTS.md](https://github.com/openai/agents.md)** — the 60k+ project standard for cross-agent context files.
- **[Hermes Agent](https://github.com/apcjoaofilho/hermes-agent)** — the agent runtime where the v1.0 prototype lived.

This framework is not a replacement for any of them. It is a thin coordination layer that lets all of these patterns play together.

---

## License

MIT. See [LICENSE](LICENSE).
