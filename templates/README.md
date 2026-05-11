# templates/

Copy-paste artifacts users drop into their projects. Each template:

1. Validates against `scripts/validate-templates.py` (planned).
2. Documents its placeholders in a header comment.
3. Has a corresponding usage section in the relevant `references/phase-*.md`.

## Template files (v2.0)

- `STATUS.md` — narrative, human-first.
- `STATE.json` — machine-readable state; validates against `references/state-schema.json`.
- `AGENTS.md` — project root template.
- `ADR.md` — Architecture Decision Record.
- `spec-delta.md` — per-change spec, manual engine fallback only.
- `project.md` — source-of-truth spec, manual engine fallback only.
- `cron-pipeline-manager.txt` — multi-project cron prompt skeleton; completed in M5.
- `cron-single-project.txt` — single-project cron prompt skeleton; completed in M5.
- `handoff-schema.yaml` — deferred to M12, where `scripts/handoff.py` validates it.
- `gates/` — one YAML per phase, deferred to M6 for the machine-verifiable gate schema.

See [PLAN.md §3.1](../PLAN.md#31-repository-layout) for the canonical inventory.
