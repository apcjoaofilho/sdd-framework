import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "advance-pipeline.py"
EXAMPLE = REPO_ROOT / "examples" / "greenfield-cli-tool"
NOW = "2026-05-12T12:00:00Z"


def run_advance(project_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(project_root),
            "--framework-root",
            str(REPO_ROOT),
            "--now",
            NOW,
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def copy_example(tmp_path: Path) -> Path:
    project_root = tmp_path / "greenfield-cli-tool"
    shutil.copytree(EXAMPLE, project_root)
    return project_root


def read_state(project_root: Path) -> dict:
    return json.loads((project_root / "STATE.json").read_text(encoding="utf-8"))


def test_advance_pipeline_passes_research_gate_and_updates_state(tmp_path: Path) -> None:
    project_root = copy_example(tmp_path)

    result = run_advance(project_root)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["gate_result"] == "pass"
    assert payload["phase"] == "SPEC"
    assert payload["state_changes"] == {"phase": "SPEC", "retry_count": 0}

    state = read_state(project_root)
    assert state["phase"] == "SPEC"
    assert state["retry_count"] == 0
    assert state["last_error"] is None
    assert state["last_update"] == NOW
    assert state["last_agent"] == "advance-pipeline"
    assert state["next_step"] == "Draft the CLI tool spec from the accepted research direction."


def test_advance_pipeline_updates_status_history(tmp_path: Path) -> None:
    project_root = copy_example(tmp_path)

    result = run_advance(project_root)

    assert result.returncode == 0, result.stdout + result.stderr
    status = (project_root / "STATUS.md").read_text(encoding="utf-8")
    assert "- Phase: SPEC" in status
    assert "- Updated at: 2026-05-12T12:00:00Z" in status
    assert "| 2026-05-12 | SPEC | Advanced from RESEARCH to SPEC. | advance-pipeline |" in status


def test_advance_pipeline_fails_and_increments_retry_count(tmp_path: Path) -> None:
    project_root = copy_example(tmp_path)
    evidence_path = project_root / ".sdd" / "gates" / "research.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["checks"]["citations_present"] = False
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    result = run_advance(project_root)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["gate_result"] == "fail"
    assert payload["failing_checks"] == ["citations_present must be true"]

    state = read_state(project_root)
    assert state["phase"] == "RESEARCH"
    assert state["retry_count"] == 1
    assert state["last_error"] == "citations_present must be true"
    assert state["next_step"] == "Fix gate evidence: citations_present must be true"


def test_advance_pipeline_blocks_after_third_failed_retry(tmp_path: Path) -> None:
    project_root = copy_example(tmp_path)
    state = read_state(project_root)
    state["retry_count"] = 2
    (project_root / "STATE.json").write_text(
        json.dumps(state, indent=2) + "\n",
        encoding="utf-8",
    )
    evidence_path = project_root / ".sdd" / "gates" / "research.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["checks"]["research_doc_exists"] = False
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    result = run_advance(project_root)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["gate_result"] == "blocked"

    state = read_state(project_root)
    assert state["phase"] == "BLOCKED"
    assert state["retry_count"] == 3
    assert state["last_error"] == "research_doc_exists must be true"
