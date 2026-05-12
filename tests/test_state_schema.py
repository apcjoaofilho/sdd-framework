import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = REPO_ROOT / "references" / "state-schema.json"
STATE_TEMPLATE = REPO_ROOT / "templates" / "STATE.json"


def test_state_template_validates_against_schema() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    state = json.loads(STATE_TEMPLATE.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    errors = sorted(validator.iter_errors(state), key=lambda item: list(item.path))

    assert errors == []


def test_schema_covers_spec_engine_and_handoff_backend_enums() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert schema["properties"]["spec_engine"]["enum"] == ["openspec", "manual"]
    assert schema["properties"]["handoff_backend"]["enum"] == [
        "local",
        "github",
        "gitlab",
    ]
