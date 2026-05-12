#!/usr/bin/env python3
"""Advance one SDD project phase when the current gate evidence passes."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_RUNTIME_ERROR = 2

PHASE_SEQUENCE = [
    "RESEARCH",
    "DISCUSS",
    "SPEC",
    "PLAN",
    "EXECUTE",
    "VERIFY",
    "REVIEW",
    "RELEASE",
    "ARCHIVE",
]


class PipelineError(Exception):
    """User-correctable pipeline input error."""


class GateValidationError(PipelineError):
    """Gate evidence failed validation."""

    def __init__(self, failures: list[str]) -> None:
        self.failures = failures
        super().__init__("gate validation failed")


def parse_args(argv: list[str]) -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Advance a project when templates/gates/<phase>.yaml passes."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root containing STATE.json and STATUS.md",
    )
    parser.add_argument(
        "--framework-root",
        type=Path,
        default=repo_root,
        help="SDD Framework root containing templates/gates",
    )
    parser.add_argument(
        "--now",
        default=None,
        help="Override current UTC time for deterministic tests",
    )
    parser.add_argument(
        "--format",
        choices=("tty", "json"),
        default="json",
        help="Output format",
    )
    return parser.parse_args(argv)


def parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path, kind: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PipelineError(f"{kind} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PipelineError(f"invalid {kind}: {exc.msg}") from exc
    except OSError as exc:
        raise PipelineError(f"could not read {kind}: {exc}") from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    try:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise PipelineError(f"could not write {path}: {exc}") from exc


def current_phase(state: dict[str, Any]) -> str:
    phase = state.get("phase")
    if not isinstance(phase, str) or not phase:
        raise PipelineError("STATE.json phase must be a non-empty string")
    return phase


def gate_path(framework_root: Path, phase: str) -> Path:
    return framework_root / "templates" / "gates" / f"{phase.lower()}.yaml"


def evidence_path(project_root: Path, phase: str) -> Path:
    return project_root / ".sdd" / "gates" / f"{phase.lower()}.json"


def normalize_evidence(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PipelineError("gate evidence must be a JSON object")
    checks = payload.get("checks", payload)
    if not isinstance(checks, dict):
        raise PipelineError("gate evidence checks must be a JSON object")
    return checks


def validate_check(name: str, spec: dict[str, Any], value: Any) -> list[str]:
    failures = []
    check_type = spec.get("type")

    if check_type == "boolean":
        if not isinstance(value, bool):
            return [f"{name} must be a boolean"]
        if spec.get("required") is True and value is not True:
            failures.append(f"{name} must be true")
        return failures

    if check_type == "enum":
        values = spec.get("values")
        if not isinstance(values, list) or value not in values:
            failures.append(f"{name} must be one of {values!r}")
        return failures

    if check_type == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            return [f"{name} must be an integer"]
        minimum = spec.get("minimum")
        maximum = spec.get("maximum")
        if isinstance(minimum, int) and value < minimum:
            failures.append(f"{name} must be >= {minimum}")
        if isinstance(maximum, int) and value > maximum:
            failures.append(f"{name} must be <= {maximum}")
        return failures

    return [f"{name} has unsupported gate type {check_type!r}"]


def validate_gate(gate: Any, checks: dict[str, Any]) -> tuple[str, list[str]]:
    if not isinstance(gate, dict):
        raise PipelineError("gate file must be a JSON object")
    gate_checks = gate.get("checks")
    if not isinstance(gate_checks, dict) or not gate_checks:
        raise PipelineError("gate file must contain a non-empty checks object")

    failures = []
    for name, raw_spec in gate_checks.items():
        if not isinstance(raw_spec, dict):
            failures.append(f"{name} gate definition must be an object")
            continue
        if name not in checks:
            if raw_spec.get("required") is True:
                failures.append(f"{name} is required")
            continue
        failures.extend(validate_check(name, raw_spec, checks[name]))

    next_phase = checks.get("next_phase")
    if isinstance(next_phase, str) and next_phase == "BLOCKED":
        failures.append("next_phase is BLOCKED")

    if failures:
        raise GateValidationError(failures)

    if isinstance(next_phase, str):
        return next_phase, []
    return default_next_phase(str(gate.get("phase", ""))), []


def default_next_phase(phase: str) -> str:
    try:
        index = PHASE_SEQUENCE.index(phase)
    except ValueError as exc:
        raise PipelineError(f"unknown phase: {phase}") from exc
    if index == len(PHASE_SEQUENCE) - 1:
        return "ARCHIVE"
    return PHASE_SEQUENCE[index + 1]


def update_status(
    status_path: Path,
    *,
    old_phase: str,
    new_phase: str,
    next_step: str,
    now: datetime,
    agent: str,
) -> None:
    try:
        lines = status_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise PipelineError(f"STATUS.md not found: {status_path}") from exc
    except OSError as exc:
        raise PipelineError(f"could not read STATUS.md: {exc}") from exc

    updated = []
    for line in lines:
        if line.startswith("- Phase:"):
            updated.append(f"- Phase: {new_phase}")
        elif line.startswith("- Next step:"):
            updated.append(f"- Next step: {next_step}")
        elif line.startswith("- Blockers:"):
            updated.append("- Blockers: none")
        elif line.startswith("- Updated at:"):
            updated.append(f"- Updated at: {iso_z(now)}")
        else:
            updated.append(line)

    history_row = (
        f"| {now.date().isoformat()} | {new_phase} | "
        f"Advanced from {old_phase} to {new_phase}. | {agent} |"
    )
    insert_at = find_history_insert_at(updated)
    updated.insert(insert_at, history_row)

    try:
        status_path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")
    except OSError as exc:
        raise PipelineError(f"could not write STATUS.md: {exc}") from exc


def find_history_insert_at(lines: list[str]) -> int:
    try:
        history_index = lines.index("## History")
    except ValueError:
        return len(lines)

    index = history_index + 1
    while index < len(lines):
        if index > history_index + 1 and lines[index].startswith("## "):
            return index
        index += 1
    return len(lines)


def apply_pass(
    project_root: Path,
    state: dict[str, Any],
    *,
    old_phase: str,
    new_phase: str,
    checks: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    next_step = str(checks.get("next_step") or f"Begin {new_phase} phase.")
    agent = "advance-pipeline"
    state.update(
        {
            "phase": new_phase,
            "next_step": next_step,
            "last_update": iso_z(now),
            "last_agent": agent,
            "retry_count": 0,
            "last_error": None,
        }
    )
    write_json(project_root / "STATE.json", state)
    update_status(
        project_root / "STATUS.md",
        old_phase=old_phase,
        new_phase=new_phase,
        next_step=next_step,
        now=now,
        agent=agent,
    )
    return state


def apply_failure(
    project_root: Path,
    state: dict[str, Any],
    *,
    failures: list[str],
    now: datetime,
) -> dict[str, Any]:
    retry_count = int(state.get("retry_count", 0)) + 1
    next_step = f"Fix gate evidence: {failures[0]}"
    state.update(
        {
            "next_step": next_step,
            "last_update": iso_z(now),
            "last_agent": "advance-pipeline",
            "retry_count": retry_count,
            "last_error": "; ".join(failures),
        }
    )
    if retry_count >= 3:
        state["phase"] = "BLOCKED"
    write_json(project_root / "STATE.json", state)
    return state


def result_payload(
    *,
    project_root: Path,
    phase: str | None,
    gate_result: str,
    failing_checks: list[str],
    next_step: str | None,
    state_changes: dict[str, Any],
) -> dict[str, Any]:
    return {
        "project_root": str(project_root),
        "phase": phase,
        "gate_result": gate_result,
        "failing_checks": failing_checks,
        "next_step": next_step,
        "state_changes": state_changes,
    }


def emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2))
        return
    print(f"{payload['gate_result']}: {payload.get('next_step') or ''}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    project_root = args.project_root.resolve()
    framework_root = args.framework_root.resolve()

    try:
        now = parse_utc(args.now) if args.now else datetime.now(timezone.utc)
        state = load_json(project_root / "STATE.json", "STATE.json")
        if not isinstance(state, dict):
            raise PipelineError("STATE.json must be a JSON object")
        phase = current_phase(state)
        if phase == "BLOCKED":
            payload = result_payload(
                project_root=project_root,
                phase=phase,
                gate_result="blocked",
                failing_checks=["project is already BLOCKED"],
                next_step=state.get("next_step"),
                state_changes={},
            )
            emit(payload, args.format)
            return EXIT_USER_ERROR

        gate = load_json(gate_path(framework_root, phase), f"{phase} gate")
        evidence = normalize_evidence(load_json(evidence_path(project_root, phase), f"{phase} gate evidence"))
        new_phase, _ = validate_gate(gate, evidence)
        updated_state = apply_pass(
            project_root,
            state,
            old_phase=phase,
            new_phase=new_phase,
            checks=evidence,
            now=now,
        )
        payload = result_payload(
            project_root=project_root,
            phase=new_phase,
            gate_result="pass",
            failing_checks=[],
            next_step=updated_state.get("next_step"),
            state_changes={"phase": new_phase, "retry_count": 0},
        )
        emit(payload, args.format)
        return EXIT_SUCCESS
    except GateValidationError as exc:
        updated_state = apply_failure(project_root, state, failures=exc.failures, now=now)
        gate_result = "blocked" if updated_state.get("phase") == "BLOCKED" else "fail"
        payload = result_payload(
            project_root=project_root,
            phase=updated_state.get("phase"),
            gate_result=gate_result,
            failing_checks=exc.failures,
            next_step=updated_state.get("next_step"),
            state_changes={
                "phase": updated_state.get("phase"),
                "retry_count": updated_state.get("retry_count"),
            },
        )
        emit(payload, args.format)
        return EXIT_USER_ERROR
    except (PipelineError, ValueError) as exc:
        payload = result_payload(
            project_root=project_root,
            phase=None,
            gate_result="blocked",
            failing_checks=[str(exc)],
            next_step=None,
            state_changes={},
        )
        emit(payload, args.format)
        return EXIT_USER_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
