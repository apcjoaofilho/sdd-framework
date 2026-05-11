# skill/

Hermes Agent adapter(s). One subdirectory per skill.

The adapter is intentionally **thin**: it links into `../references/` and `../templates/` rather than duplicating their content. If you find yourself copying logic from the framework into the skill, stop and put the logic in the framework instead.

## Planned (v2.0)

- `spec-driven-dev/SKILL.md` — main pipeline skill, replaces the v1.0 standalone skill.

Future adapters (post-v2.0):

- Codex CLI adapter (if upstream allows skill-like extensions).
- Cursor adapter.
- Aider adapter.
