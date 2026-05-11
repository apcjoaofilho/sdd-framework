# scripts/

Python tooling that consumers and CI both use.

## Conventions

- **Python 3.10+.** No third-party runtime dependencies by default. If a script needs one, it must be optional and documented.
- **Each script ships with tests** in `tests/scripts/test_<name>.py`.
- **Scripts are executable** (`chmod +x`) and start with `#!/usr/bin/env python3`.
- **Output is JSON or TTY-friendly** — controlled by `--format json` flag.
- **Exit codes matter.** `0` success, `1` user error, `2` runtime error, `64+` script-specific.

## Planned files (v2.0)

| Script | Purpose | Roadmap ID |
|--------|---------|------------|
| `check-status.py` | Watchdog — reads `~/.sdd/projects.yaml`, returns JSON of phase/lock/staleness | M2 |
| `advance-pipeline.py` | Cron `--script` preprocessor; decides which project to advance | M5 |
| `validate-templates.py` | CI — every template in `templates/` validates | M1 |
| `onboard.py` | Bootstraps an existing project (detects stack, generates STATUS/STATE/AGENTS) | S3 |
| `rollback.py` | Moves a project back one phase, audit-logged | N4-prereq |
| `acquire-lock.py` | Multi-agent lock acquire/release/check | S5 |
| `handoff.py` | Pluggable handoff backend (`local` default + `github` opt-in). Subcommands: `acquire`, `release`, `notify`, `list`, `migrate-backend` | M12 |
| `migrate.py` | v1.0 → v2.0 upgrade for existing prototype users | N4 |
| `bootstrap-portability.sh` | Symlinks/copies for cross-agent files (POSIX + Windows-aware) | N5 |
| `spawn-worktree.sh` | Worktree-by-default helper for parallel EXECUTE | S4 |

See [PLAN.md §3.1](../PLAN.md#31-repository-layout) for the canonical inventory.
