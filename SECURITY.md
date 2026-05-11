# Security Policy

## Supported versions

The project is in pre-release planning. There is no `v1.x` to support — `v2.0.0` will be the first tagged release. Until then:

| Version           | Supported          |
|-------------------|--------------------|
| `main` (unreleased) | ✅ best effort   |

After v2.0.0 ships, the latest minor will receive security fixes; older minors are best-effort.

---

## Reporting a vulnerability

**Do not open a public issue for security problems.**

Email **joao.the@gmail.com** with:

- A description of the issue.
- Steps to reproduce.
- Affected files / scripts / templates.
- Your assessment of impact.
- (Optional) a suggested fix.

You will receive an acknowledgement within **72 hours**. We aim to publish a fix within **14 days** for critical issues, longer for low-severity ones. Coordinated disclosure is welcome.

---

## What counts as a vulnerability

Examples in scope:

- A script in `scripts/` that executes attacker-controlled input (command injection, path traversal).
- A template that, when copied verbatim, exposes secrets or weakens git hygiene.
- A cron prompt template that, when run, exfiltrates project contents to an unintended destination.
- An adapter (`skill/`) that bypasses Hermes' authorization model.

Examples **out of scope**:

- Issues in upstream tools (Hermes Agent, Claude Code, Codex CLI). Report those upstream.
- The framework's templates exposing data the user explicitly placed in `STATUS.md` or `STATE.json`. Treat those files as project-public.
- Findings that require an attacker who already has write access to the repo or to the operator's machine.

---

## Hardening recommendations for operators

- **Never commit secrets** to `STATUS.md`, `STATE.json`, or any artifact in `openspec/`. Treat all SDD-generated files as readable by every contributor.
- **Review cron prompts** before scheduling. Cron sessions have zero chat history — a malicious prompt has full agent privileges.
- **Lock files have TTL, not enforcement.** Use repo branch protection if you need stronger isolation between agents.
- **Pin script versions** when running in CI. The framework will tag releases; depend on tags, not `main`.

---

## Credits

Reporters who follow coordinated disclosure will be credited in `CHANGELOG.md` (opt-in) once v2.0.0 ships.
