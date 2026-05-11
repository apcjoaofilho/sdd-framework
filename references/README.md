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
- `borrowed/` — engineering-technique docs forked from `agent-skills` (MIT), with attribution; see [`borrowed/README.md`](borrowed/README.md) for the policy

See [PLAN.md §3.1](../PLAN.md#31-repository-layout) for the canonical inventory.
