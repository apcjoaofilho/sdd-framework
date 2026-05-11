import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate-state.py"
SCHEMA = REPO_ROOT / "references" / "state-schema.json"


VALID_STATE = {
    "phase": "EXECUTE",
    "next_step": "Task 4 of 12 - implement message parser",
    "spec": "openspec/changes/0003-multi-channel/spec.md",
    "plan": ".sdd/plans/2026-05-11-multi-channel.md",
    "branch": "feat/multi-channel",
    "worktree": "/home/joao/projects/foo-multi-channel",
    "last_commit": "a1b2c3d",
    "last_agent": "claude-code",
    "last_update": "2026-05-11T14:32:00Z",
    "lock": {
        "agent": "codex-cli",
        "started_at": "2026-05-11T14:30:00Z",
        "ttl_minutes": 30,
    },
    "retry_count": 0,
    "last_error": None,
    "flavor": "software",
    "spec_engine": "openspec",
    "handoff_backend": "local",
}


def write_state(tmp_path: Path, data: dict) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "STATE.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def run_validator(
    path: Path, *, output_format: str = "tty"
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(path),
            "--schema",
            str(SCHEMA),
            "--format",
            output_format,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_state_passes(tmp_path: Path) -> None:
    state_path = write_state(tmp_path, VALID_STATE)

    result = run_validator(state_path)

    assert result.returncode == 0
    assert "valid" in result.stdout.lower()
    assert result.stderr == ""


def test_json_format_reports_valid_state(tmp_path: Path) -> None:
    state_path = write_state(tmp_path, VALID_STATE)

    result = run_validator(state_path, output_format="json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload == {"ok": True, "path": str(state_path), "errors": []}


def test_missing_required_field_rejects(tmp_path: Path) -> None:
    invalid_state = dict(VALID_STATE)
    invalid_state.pop("phase")
    state_path = write_state(tmp_path, invalid_state)

    result = run_validator(state_path, output_format="json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any("phase" in error["message"] for error in payload["errors"])


def test_unknown_field_rejects(tmp_path: Path) -> None:
    invalid_state = dict(VALID_STATE, unexpected="not allowed")
    state_path = write_state(tmp_path, invalid_state)

    result = run_validator(state_path, output_format="json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert any("unexpected" in error["message"] for error in payload["errors"])


def test_invalid_json_rejects_as_user_error(tmp_path: Path) -> None:
    state_path = tmp_path / "STATE.json"
    state_path.write_text("{not json}\n", encoding="utf-8")

    result = run_validator(state_path, output_format="json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["errors"][0]["type"] == "json"


def test_bad_field_variants_reject(tmp_path: Path) -> None:
    bad_variants = {
        "phase": {"phase": "BUILD"},
        "next_step": {"next_step": 42},
        "spec": {"spec": 42},
        "plan": {"plan": 42},
        "branch": {"branch": 42},
        "worktree": {"worktree": 42},
        "last_commit": {"last_commit": 42},
        "last_agent": {"last_agent": 42},
        "last_update": {"last_update": "not-a-date-time"},
        "lock": {"lock": None},
        "lock.agent": {"lock": {**VALID_STATE["lock"], "agent": 42}},
        "lock.started_at": {
            "lock": {**VALID_STATE["lock"], "started_at": "not-a-date-time"}
        },
        "lock.ttl_minutes": {"lock": {**VALID_STATE["lock"], "ttl_minutes": 0}},
        "retry_count": {"retry_count": -1},
        "last_error": {"last_error": 42},
        "flavor": {"flavor": "mobile"},
        "spec_engine": {"spec_engine": "custom"},
        "handoff_backend": {"handoff_backend": "jira"},
    }

    for field, patch in bad_variants.items():
        invalid_state = {**VALID_STATE, **patch}
        state_path = write_state(tmp_path / field.replace(".", "_"), invalid_state)

        result = run_validator(state_path, output_format="json")

        assert result.returncode == 1, field
        payload = json.loads(result.stdout)
        assert payload["ok"] is False, field
        assert payload["errors"], field
