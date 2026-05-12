import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "templates"
SCRIPT = REPO_ROOT / "scripts" / "validate-templates.py"
SCHEMA = REPO_ROOT / "references" / "state-schema.json"

EXPECTED_TEMPLATES = [
    "STATUS.md",
    "STATE.json",
    "AGENTS.md",
    "ADR.md",
    "spec-delta.md",
    "project.md",
    "cron-pipeline-manager.txt",
    "cron-single-project.txt",
    "handoff-schema.yaml",
]

EXPECTED_GATES = [
    "research.yaml",
    "discuss.yaml",
    "spec.yaml",
    "plan.yaml",
    "execute.yaml",
    "verify.yaml",
    "review.yaml",
    "release.yaml",
    "archive.yaml",
]

COMMENT_PREFIXES = {
    ".md": "<!--",
    ".txt": "#",
    ".yaml": "#",
}


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_expected_templates_exist() -> None:
    for relative_path in EXPECTED_TEMPLATES:
        assert (TEMPLATES_DIR / relative_path).is_file(), relative_path


def test_text_templates_start_with_placeholder_header() -> None:
    for relative_path in EXPECTED_TEMPLATES:
        path = TEMPLATES_DIR / relative_path
        if path.suffix in {".json", ".yaml"}:
            continue

        first_line = path.read_text(encoding="utf-8").splitlines()[0]

        assert first_line.startswith(COMMENT_PREFIXES[path.suffix]), relative_path
        assert "Placeholders:" in first_line, relative_path


def test_expected_gates_exist_and_parse() -> None:
    for relative_path in EXPECTED_GATES:
        path = TEMPLATES_DIR / "gates" / relative_path

        assert path.is_file(), relative_path
        payload = json.loads(path.read_text(encoding="utf-8"))

        assert payload["phase"] == path.stem.upper()
        assert payload["checks"]
        for check in payload["checks"].values():
            assert check["type"] in {"boolean", "enum", "integer"}


def test_handoff_schema_exists_and_parses() -> None:
    path = TEMPLATES_DIR / "handoff-schema.yaml"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert set(payload["handoff"]) == {
        "id",
        "from_agent",
        "to_agent",
        "phase",
        "context_link",
        "gate_passed",
        "decisions",
        "created_at",
        "status",
    }


def test_state_template_validates_against_schema() -> None:
    state_path = TEMPLATES_DIR / "STATE.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "validate-state.py"),
            str(state_path),
            "--schema",
            str(SCHEMA),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_manual_engine_fallback_templates_are_labelled() -> None:
    for relative_path in ("spec-delta.md", "project.md"):
        content = (TEMPLATES_DIR / relative_path).read_text(encoding="utf-8")
        assert "manual engine fallback only" in content.lower()
        assert "openspec" in content.lower()


def test_validate_templates_script_passes() -> None:
    result = run_validator("--format", "json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["errors"] == []
    assert set(payload["checked"]) >= set(EXPECTED_TEMPLATES)


def test_validate_templates_reports_missing_template(tmp_path: Path) -> None:
    result = run_validator(
        "--templates-dir",
        str(tmp_path),
        "--schema",
        str(SCHEMA),
        "--format",
        "json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any(error["type"] == "missing" for error in payload["errors"])
