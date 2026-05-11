# templates/

Copy-paste artifacts users drop into their projects. Each template:

1. Validates against `scripts/validate-templates.py` (planned).
2. Documents its placeholders in a header comment.
3. Has a corresponding usage section in the relevant `references/phase-*.md`.

## Planned files (v2.0)

- `STATUS.md` — narrative, human-first.
- `STATE.json` — machine-readable state.
- `AGENTS.md` — project root template.
- `ADR.md` — Architecture Decision Record.
- `spec-delta.md` — per-change spec.
- `project.md` — source-of-truth spec.
- `cron-pipeline-manager.txt` — multi-project cron prompt.
- `cron-single-project.txt` — single-project cron prompt.
- `gates/` — one YAML per phase, machine-verifiable.

See [PLAN.md §3.1](../PLAN.md#31-repository-layout) for the canonical inventory.
