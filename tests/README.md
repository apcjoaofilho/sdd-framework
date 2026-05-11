# tests/

Test suite for `scripts/`, template validation, and JSON Schema checks.

## Layout

```
tests/
├── scripts/         one test_<name>.py per script
├── templates/       schema/structure tests for templates/
└── conftest.py      shared fixtures
```

Run with `pytest`. CI enforces this on every PR (workflow added in M1).
