# references/

Long-form documentation. Each file is referenced from a short overview elsewhere (the Hermes skill, top-level README, or PLAN.md) and goes deep on one topic.

## Planned files (v2.0)

- `phase-research.md`
- `phase-discuss.md`
- `phase-spec.md`
- `phase-plan.md`
- `phase-execute.md`
- `phase-verify.md`
- `phase-review.md`
- `phase-release.md`
- `phase-archive.md`
- `phase-observe.md` *(optional flavor)*
- `portability-matrix.md` — agent × file × format compatibility
- `integration-orchestrator.md` — playbook for `development-orchestrator-joao`
- `integration-cron.md` — Hermes Agent cron tooling alignment
- `integration-openspec.md` — OpenSpec as default SPEC/APPLY/ARCHIVE engine; phase-to-command map; `manual` fallback contract
- `handoff-backends.md` — pluggable handoff/discussion backends (`local` default + `github` opt-in); tradeoff and mention discipline
- `state-schema.json` — JSON Schema for `STATE.json`

## Template inventory

The reusable templates live under [`../templates/`](../templates/):

- `STATUS.md` — human-readable project status.
- `STATE.json` — machine-readable phase state validated by `state-schema.json`.
- `AGENTS.md` — portable agent instructions for a project root.
- `ADR.md` — Architecture Decision Record.
- `spec-delta.md` and `project.md` — manual engine fallback only; OpenSpec owns native spec artifacts when `spec_engine = openspec`.
- `cron-pipeline-manager.txt` and `cron-single-project.txt` — skeletal cron prompt templates completed in M5.
- `handoff-schema.yaml` is deferred to M12.
- `templates/gates/*.yaml` are deferred to M6.
- `borrowed/` — engineering-technique docs forked from `agent-skills` (MIT), with attribution; see [`borrowed/README.md`](borrowed/README.md) for the policy

See [PLAN.md §3.1](../PLAN.md#31-repository-layout) for the canonical inventory.
