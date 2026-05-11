# SDD Framework

> The framework's own AGENTS.md — dogfood for the standard we ship.

## Description

Portable, agent-agnostic spec-driven development pipeline. Templates, scripts, and a thin Hermes Agent skill adapter. See [`PLAN.md`](PLAN.md) for the v2.0 roadmap and acceptance criteria.

## Stack

- **Language:** Python 3.10+ (scripts), Bash (bootstrap), Markdown + YAML + JSON (artifacts).
- **No runtime dependencies** for `scripts/` by default — keeps install friction low.
- **Dev tooling:** `pytest`, `ruff`, `jsonschema`, `yamllint`.

## Commands

| Action | Command |
|--------|---------|
| Install dev deps | `pip install -e ".[dev]"` *(once `pyproject.toml` lands)* |
| Lint | `ruff check .` |
| Test | `pytest` |
| Validate templates | `python scripts/validate-templates.py` *(planned)* |
| Validate STATE.json schema | `python -m jsonschema -i STATE.json references/state-schema.json` *(planned)* |

## Structure

- `PLAN.md` — v2.0 roadmap. Lives at root until v2.0 ships, then moves to `docs/history/`.
- `references/` — long-form docs (one per pipeline phase + integration guides).
- `templates/` — copy-paste artifacts users drop into their projects.
- `scripts/` — Python tooling that consumers and CI both run.
- `skill/spec-driven-dev/` — Hermes Agent adapter; thin wrapper around `references/`.
- `examples/` — runnable end-to-end demos.
- `.github/` — workflows, issue templates, PR template.

## Conventions

- **Source of truth lives in the repo.** Never put load-bearing context only in chat history or agent memory.
- **TDD for scripts.** Every script in `scripts/` has tests in `tests/scripts/`.
- **Semantic commits.** `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`. Scope optional.
- **One feature per PR.** Squash-merge into `main`. PR body links the tracking issue.
- **English only** in committed artifacts (code, docs, commits, issues, PRs). Discussion in issues can be bilingual.
- **No emoji in committed files** unless the file is explicitly a user-facing UI artifact.
- **Templates must validate.** Adding a template requires updating `scripts/validate-templates.py`.

## Pipeline status (this repo)

This project uses its own framework as soon as v2.0 acceptance criteria allow self-hosting. Until then:

- **Phase:** PLAN
- **Source of truth:** [`PLAN.md`](PLAN.md)
- **Tracking:** GitHub Milestones (`Must Have v2.0`, `Should Have v2.0`, `Nice to Have`)

Once `scripts/onboard.py` is functional (M2 + S3), this repo will gain `STATUS.md` and `STATE.json` and stop relying on PLAN.md as the only state.

## Links

- **Roadmap:** [`PLAN.md`](PLAN.md)
- **How to contribute:** [`CONTRIBUTING.md`](CONTRIBUTING.md)
- **Security disclosures:** [`SECURITY.md`](SECURITY.md)
- **Inspiration & prior art:** see [README.md → Inspiration](README.md#inspiration)

## Notes for AI agents

- **Read `PLAN.md` first.** It is the only place where v2.0 scope is authoritative.
- **Do not silently extend scope.** New phases, templates, or scripts require a PR to `PLAN.md` first.
- **Do not add Hermes-specific assumptions to `references/` or `templates/`.** Hermes integration belongs in `skill/spec-driven-dev/` and `references/integration-cron.md`.
- **Tests before implementation.** Per repo convention, scripts ship with tests in the same PR.
