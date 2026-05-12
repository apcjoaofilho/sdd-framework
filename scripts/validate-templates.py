#!/usr/bin/env python3
"""Validate framework-owned templates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_RUNTIME_ERROR = 2

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

MANUAL_FALLBACK_TEMPLATES = ["spec-delta.md", "project.md"]


class RuntimeDependencyError(Exception):
    """Required validation dependency is missing or failed."""


def parse_args(argv: list[str]) -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate SDD Framework templates.")
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=repo_root / "templates",
        help="Path to the templates directory",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=repo_root / "references" / "state-schema.json",
        help="Path to the STATE.json schema",
    )
    parser.add_argument(
        "--format",
        choices=("tty", "json"),
        default="tty",
        help="Output format",
    )
    return parser.parse_args(argv)


def load_json(path: Path, kind: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"{kind} not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid {kind}: {exc.msg}") from exc


def validate_state_template(state_path: Path, schema_path: Path) -> list[dict[str, Any]]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError as exc:
        raise RuntimeDependencyError(
            "missing dependency 'jsonschema'; install with `pip install -e .[dev]`"
        ) from exc

    schema = load_json(schema_path, "schema")
    state = load_json(state_path, "STATE.json template")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(state), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "$"
        errors.append(
            {
                "type": "schema",
                "path": str(state_path),
                "field": path,
                "message": error.message,
            }
        )
    return errors


def validate_text_template(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return [{"type": "empty", "path": str(path), "message": "template is empty"}]

    expected_prefix = COMMENT_PREFIXES.get(path.suffix)
    if expected_prefix is None:
        return [
            {
                "type": "unsupported",
                "path": str(path),
                "message": f"unsupported template suffix: {path.suffix}",
            }
        ]

    if not lines[0].startswith(expected_prefix) or "Placeholders:" not in lines[0]:
        return [
            {
                "type": "header",
                "path": str(path),
                "message": "missing first-line placeholder header",
            }
        ]
    return []


def validate_json_compatible_yaml(path: Path, kind: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [{"type": "missing", "path": str(path), "message": f"{kind} not found"}]
    except json.JSONDecodeError as exc:
        return [
            {
                "type": "yaml",
                "path": str(path),
                "message": f"invalid JSON-compatible YAML: {exc.msg}",
            }
        ]

    if not isinstance(payload, dict):
        return [{"type": "yaml", "path": str(path), "message": f"{kind} must be a map"}]

    errors = []
    if kind == "gate":
        if not isinstance(payload.get("phase"), str):
            errors.append({"type": "gate", "path": str(path), "message": "gate missing phase"})
        checks = payload.get("checks")
        if not isinstance(checks, dict) or not checks:
            errors.append(
                {
                    "type": "gate",
                    "path": str(path),
                    "message": "gate missing non-empty checks map",
                }
            )
            return errors
        for check_name, check in checks.items():
            if not isinstance(check, dict):
                errors.append(
                    {"type": "gate", "path": str(path), "message": f"{check_name} must be a map"}
                )
                continue
            check_type = check.get("type")
            if check_type not in {"boolean", "enum", "integer"}:
                errors.append(
                    {
                        "type": "gate",
                        "path": str(path),
                        "message": f"{check_name} has unsupported type {check_type!r}",
                    }
                )
            if check_type == "enum" and not check.get("values"):
                errors.append(
                    {"type": "gate", "path": str(path), "message": f"{check_name} enum must declare values"}
                )
    elif kind == "handoff schema":
        if not isinstance(payload.get("handoff"), dict):
            errors.append(
                {"type": "handoff-schema", "path": str(path), "message": "handoff schema missing handoff map"}
            )
    return errors


def validate_templates(templates_dir: Path, schema_path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    checked = []
    errors = []

    for relative_path in EXPECTED_TEMPLATES:
        path = templates_dir / relative_path
        if not path.is_file():
            errors.append({"type": "missing", "path": str(path), "message": "template not found"})
            continue
        checked.append(relative_path)
        try:
            if path.suffix == ".json":
                errors.extend(validate_state_template(path, schema_path))
            elif path.suffix == ".yaml":
                errors.extend(validate_json_compatible_yaml(path, "handoff schema"))
            else:
                errors.extend(validate_text_template(path))
        except (FileNotFoundError, ValueError) as exc:
            errors.append({"type": "parse", "path": str(path), "message": str(exc)})

    gates_dir = templates_dir / "gates"
    for relative_path in EXPECTED_GATES:
        path = gates_dir / relative_path
        if not path.is_file():
            errors.append({"type": "missing", "path": str(path), "message": "gate not found"})
            continue
        checked.append(f"gates/{relative_path}")
        errors.extend(validate_json_compatible_yaml(path, "gate"))

    for relative_path in MANUAL_FALLBACK_TEMPLATES:
        path = templates_dir / relative_path
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8").lower()
        if "manual engine fallback only" not in content or "openspec" not in content:
            errors.append(
                {
                    "type": "manual-fallback-label",
                    "path": str(path),
                    "message": "manual fallback template must mention OpenSpec and manual engine fallback only",
                }
            )

    return checked, errors


def emit_json(ok: bool, checked: list[str], errors: list[dict[str, Any]]) -> None:
    print(json.dumps({"ok": ok, "checked": checked, "errors": errors}, indent=2))


def emit_tty(ok: bool, checked: list[str], errors: list[dict[str, Any]]) -> None:
    if ok:
        print(f"valid templates: {len(checked)} checked")
        return

    print("invalid templates")
    for error in errors:
        print(f"- {error['path']}: {error['message']}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        checked, errors = validate_templates(args.templates_dir, args.schema)
    except RuntimeDependencyError as exc:
        errors = [{"type": "runtime", "path": "$", "message": str(exc)}]
        if args.format == "json":
            emit_json(False, [], errors)
        else:
            print(f"error: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR

    if errors:
        if args.format == "json":
            emit_json(False, checked, errors)
        else:
            emit_tty(False, checked, errors)
        return EXIT_USER_ERROR

    if args.format == "json":
        emit_json(True, checked, [])
    else:
        emit_tty(True, checked, [])
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
