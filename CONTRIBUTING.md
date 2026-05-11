# Contributing to SDD Framework

Thanks for considering a contribution. This document explains how to set up the repo, the conventions we follow, and the proposal flow for non-trivial changes.

---

## Ground rules

- **Read [`PLAN.md`](PLAN.md) before opening a PR.** It defines what is in scope for v2.0 and what is parked.
- **One concern per PR.** A PR that touches a script *and* renames a template *and* edits docs is three PRs.
- **English in committed artifacts.** Discussion in issues can be bilingual; commits, code, docs, PR descriptions are English.
- **No vendor lock-in.** Anything outside `skill/` must work without Hermes Agent installed.

---

## Local setup

```bash
git clone https://github.com/apcjoaofilho/sdd-framework.git
cd sdd-framework

# Once pyproject.toml lands (M1):
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Until then, the only requirement is Python 3.10+. Scripts have no third-party runtime deps.

---

## Branch and commit style

- Branch from `main`, name `feat/<short-slug>`, `fix/<short-slug>`, `docs/<short-slug>`, etc.
- Semantic commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`. Scope optional (`feat(scripts): ...`).
- Squash-merge into `main`. The squash commit body should reference the tracking issue (`Closes #42`).

---

## Proposing a non-trivial change

If your change adds or removes a phase, template, script, or flavor, open an issue first using the **Phase Improvement** template. The issue describes:

1. The motivation (what problem is unsolved today).
2. The proposed change.
3. The migration path for existing users.
4. The acceptance criteria.

Wait for one maintainer 👍 before starting implementation. Trivial fixes (typos, broken links, obvious bugs) skip this step.

---

## What needs tests

| Change type | Test required |
|-------------|---------------|
| New script in `scripts/` | Yes — `tests/scripts/test_<name>.py` |
| Modification to existing script | Yes — extend existing tests |
| New template | Yes — add to `scripts/validate-templates.py` |
| New gate YAML | Yes — schema validation |
| Documentation in `references/` | No — link checking covers it |
| README/CONTRIBUTING/SECURITY changes | No |

---

## How to propose a new pipeline phase

The pipeline is small on purpose. Adding a phase is a high-bar change.

1. Open an issue using the **Phase Improvement** template.
2. In the issue, answer: *Why can't this happen inside an existing phase?*
3. If maintainer agrees, the implementation PR must include:
   - `references/phase-<name>.md`
   - `templates/gates/<name>.yaml`
   - Update to `PLAN.md` §3.2 phase table
   - Update to `scripts/advance-pipeline.py` (recognize new phase)
   - Update to `templates/STATE.json` schema if new fields introduced

---

## How to propose a new template

1. Add file under `templates/`.
2. Add a validator entry to `scripts/validate-templates.py`.
3. Add usage docs to the relevant `references/phase-*.md` (templates without docs get rejected).
4. If the template introduces new placeholders, document each one in the file's header comment.

---

## Hermes Agent skill changes

The Hermes adapter lives at `skill/spec-driven-dev/SKILL.md`. It must remain a **thin wrapper** — it links into `references/` and `templates/`, it does not duplicate them.

- If logic belongs to the framework, put it in `references/` or `scripts/`.
- If logic is genuinely Hermes-specific (cron tool syntax, `delegate_task` parameters), it belongs in the skill.

Skill changes that duplicate framework content will be rejected.

---

## Pull request checklist

- [ ] Linked tracking issue in PR body
- [ ] Branch name follows `<type>/<slug>`
- [ ] Tests added/updated where required
- [ ] `ruff check .` passes
- [ ] `pytest` passes (when test suite exists)
- [ ] Touched files have no trailing whitespace
- [ ] No vendor lock-in introduced outside `skill/`
- [ ] `PLAN.md` updated if scope changed
- [ ] `CHANGELOG.md` entry added under `[Unreleased]`

---

## Code of Conduct

Be direct, be kind, assume good intent. No harassment, no derogatory comments. Project maintainers reserve the right to remove contributions and contributors that violate this.

---

## Maintainers

- João Filho ([@apcjoaofilho](https://github.com/apcjoaofilho))

For urgent matters or security issues, see [SECURITY.md](SECURITY.md).
