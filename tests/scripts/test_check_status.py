import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check-status.py"


def run_check_status(
    projects_file: Path, *, now: str = "2026-05-11T14:45:00Z"
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--projects-file",
            str(projects_file),
            "--now",
            now,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_state(project_root: Path, lock_started_at: str) -> None:
    project_root.mkdir(parents=True)
    state = {
        "phase": "EXECUTE",
        "next_step": "Task 4 of 12 - implement message parser",
        "spec": "openspec/changes/0003-multi-channel/spec.md",
        "plan": ".sdd/plans/2026-05-11-multi-channel.md",
        "branch": "feat/multi-channel",
        "worktree": str(project_root),
        "last_commit": "a1b2c3d",
        "last_agent": "claude-code",
        "last_update": "2026-05-11T14:32:00Z",
        "lock": {
            "agent": "codex-cli",
            "started_at": lock_started_at,
            "ttl_minutes": 30,
        },
        "retry_count": 2,
        "last_error": None,
        "flavor": "software",
        "spec_engine": "openspec",
        "handoff_backend": "local",
    }
    (project_root / "STATE.json").write_text(
        json.dumps(state, indent=2) + "\n",
        encoding="utf-8",
    )


def test_check_status_reads_projects_yaml_and_state(tmp_path: Path) -> None:
    project_root = tmp_path / "demo"
    write_state(project_root, "2026-05-11T14:30:00Z")
    projects_file = tmp_path / "projects.yaml"
    projects_file.write_text(
        f"projects:\n  - name: demo\n    path: {project_root}\n",
        encoding="utf-8",
    )

    result = run_check_status(projects_file)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["errors"] == []
    assert payload["projects"] == [
        {
            "name": "demo",
            "path": str(project_root),
            "phase": "EXECUTE",
            "branch": "feat/multi-channel",
            "lock_status": "locked",
            "retry_count": 2,
            "last_error": None,
        }
    ]


def test_check_status_marks_expired_lock_stale(tmp_path: Path) -> None:
    project_root = tmp_path / "demo"
    write_state(project_root, "2026-05-11T13:30:00Z")
    projects_file = tmp_path / "projects.yaml"
    projects_file.write_text(
        f"projects:\n  - {project_root}\n",
        encoding="utf-8",
    )

    result = run_check_status(projects_file)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["projects"][0]["name"] == "demo"
    assert payload["projects"][0]["lock_status"] == "stale"


def test_check_status_reports_missing_projects_file(tmp_path: Path) -> None:
    result = run_check_status(tmp_path / "missing.yaml")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["projects"] == []
    assert "projects file not found" in payload["errors"][0]


def test_check_status_reports_project_without_state(tmp_path: Path) -> None:
    project_root = tmp_path / "demo"
    project_root.mkdir()
    projects_file = tmp_path / "projects.yaml"
    projects_file.write_text(
        f"projects:\n  - path: {project_root}\n",
        encoding="utf-8",
    )

    result = run_check_status(projects_file)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["projects"][0]["error"] == "STATE.json not found"
