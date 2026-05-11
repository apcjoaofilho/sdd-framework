# Changelog

All notable changes to SDD Framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository scaffolding: PLAN.md (v2.0 roadmap), README, AGENTS.md (dogfooded), CONTRIBUTING, SECURITY, LICENSE (MIT).
- Empty directory structure for `references/`, `templates/`, `scripts/`, `skill/`, `examples/`, `.github/`.
- **Handoff/discussion layer** (PLAN.md §3.7): pluggable backend with `local` (default, files in `.sdd/handoffs/`) and `github` (Issues with defined label schema) shipping in v2.0; `gitlab` parked. Promoted to Must-Have **M12** based on community evidence (r/hermesagent megathread) plus deliberate vendor-tradeoff acceptance.
- **Pluggable spec engine** (PLAN.md §3.8): `spec_engine: openspec | manual`. OpenSpec is the default engine for SPEC/APPLY/ARCHIVE (framework calls the `openspec` CLI, never patches its internals); `manual` is a thin-markdown fallback that keeps the no-lock-in promise. Added Must-Haves **M10** (adopt OpenSpec) and **M11** (map 9 phases → OpenSpec commands). Resolves open question #2.
- **`references/borrowed/`**: policy for forking engineering-technique docs from `addyosmani/agent-skills` (MIT) with attribution; ≤8 files. Added Should-Have **S9** to import the first batch.
- STATE.json gains optional `handoff_backend` and `spec_engine` fields.
- Planned files: `references/handoff-backends.md`, `references/integration-openspec.md`, `templates/handoff-schema.yaml`, `scripts/handoff.py`, `references/borrowed/README.md` (created).
- Added Nice-to-Have **N9** (`gitlab` handoff backend + Forgejo/Gitea/Codeberg case-by-case).
- `docs/` directory with `IMPLEMENTATION-KICKOFF.md` (self-contained prompt to start the foundation work — M3 → M1 → M6 — in a fresh AI session) and `docs/README.md`.

### Notes
- Project is in **planning**. No tagged release yet.
- v1.0 prototype existed as a Hermes Agent skill (`spec-driven-dev`); this repo absorbs the lessons and rebuilds as a portable framework + thin Hermes adapter.
- The `local` handoff backend and the availability of `spec_engine = manual` both exist to preserve the no-vendor-lock-in principle from PLAN.md §2 — external engines (OpenSpec) and external hosts (GitHub) are recommended defaults, never hard requirements.
