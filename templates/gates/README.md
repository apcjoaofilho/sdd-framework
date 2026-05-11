# templates/gates/

Machine-verifiable acceptance gates per phase.

Each YAML file describes the criteria that must hold true before a project may advance from one phase to the next. `scripts/advance-pipeline.py` parses these and decides — without an LLM call — whether to promote a project.

## Schema (draft, finalized in M6)

```yaml
phase: <RESEARCH | DISCUSS | SPEC | PLAN | EXECUTE | VERIFY | REVIEW | RELEASE | ARCHIVE | OBSERVE>
description: <one-line summary>
required:
  - id: <short-slug>
    description: <human-readable check>
    check:
      type: <file_exists | file_contains | command_exit_zero | json_path_truthy>
      args: { ... }
optional:
  - id: <short-slug>
    description: ...
    check: { ... }
```

## Planned files (v2.0)

- `research.yaml`
- `discuss.yaml`
- `spec.yaml`
- `plan.yaml`
- `execute.yaml`
- `verify.yaml`
- `review.yaml`
- `release.yaml`
- `archive.yaml`
- `observe.yaml` *(optional flavor)*

Custom flavors will live in `templates/gates/flavors/<name>/`.
