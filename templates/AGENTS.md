<!-- Placeholders: {{PROJECT_NAME}}, {{PROJECT_DESCRIPTION}}, {{PRIMARY_LANGUAGE}}, {{TEST_COMMAND}}, {{LINT_COMMAND}}, {{SPEC_ENGINE}}, {{HANDOFF_BACKEND}} -->
# {{PROJECT_NAME}}

## Description

{{PROJECT_DESCRIPTION}}

## Stack

- Primary language: {{PRIMARY_LANGUAGE}}
- Spec engine: {{SPEC_ENGINE}}
- Handoff backend: {{HANDOFF_BACKEND}}

## Commands

- Test: `{{TEST_COMMAND}}`
- Lint: `{{LINT_COMMAND}}`

## SDD Framework files

- `STATUS.md` is the human-readable project status.
- `STATE.json` is the machine-readable pipeline state.
- `.sdd/plans/` stores implementation plans.
- OpenSpec owns `openspec/` when `spec_engine = openspec`.

## Agent rules

- Read `STATE.json` and `STATUS.md` before changing phase state.
- Keep changes within the current phase unless the gate has passed.
- Update `STATUS.md` when the phase changes or a blocker appears.
- Do not rely on chat history as the source of truth.
- Preserve portability: anything outside agent-specific folders must be usable without a specific AI tool.
