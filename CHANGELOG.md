# Changelog

All notable changes to SDD Framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository scaffolding: PLAN.md (v2.0 roadmap), README, AGENTS.md (dogfooded), CONTRIBUTING, SECURITY, LICENSE (MIT).
- Empty directory structure for `references/`, `templates/`, `scripts/`, `skill/`, `examples/`, `.github/`.
- **Handoff/discussion layer** (PLAN.md §3.7): pluggable backend with `local` (default, files in `.sdd/handoffs/`) and `github` (Issues with defined label schema) shipping in v2.0; `gitlab` parked. Promoted to Must-Have **M12** based on community evidence (r/hermesagent megathread) plus deliberate vendor-tradeoff acceptance.
- STATE.json gains optional `handoff_backend` field.
- Planned files: `references/handoff-backends.md`, `templates/handoff-schema.yaml`, `scripts/handoff.py`.

### Notes
- Project is in **planning**. No tagged release yet.
- v1.0 prototype existed as a Hermes Agent skill (`spec-driven-dev`); this repo absorbs the lessons and rebuilds as a portable framework + thin Hermes adapter.
- The `local` backend remains the default to preserve the no-vendor-lock-in principle from PLAN.md §2.
