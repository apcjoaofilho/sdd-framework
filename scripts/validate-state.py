#!/usr/bin/env python3
"""Validate SDD Framework STATE.json files against JSON Schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_RUNTIME_ERROR = 2


class StateValidationError(Exception):
    """User-correctable validation or input error."""

    def __init__(self, errors: list[dict[str, Any]]) -> None:
        self.errors = errors
        super().__init__(errors[0]["message"] if errors else "validation failed")


class RuntimeDependencyError(Exception):
    """Required validation dependency is missing or failed."""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a STATE.json file against references/state-schema.json."
    )
    parser.add_argument("state", type=Path, help="Path to STATE.json")
    parser.add_argument(
        "--schema",
        type=Path,
        default=(
            Path(__file__).resolve().parents[1] / "references" / "state-schema.json"
        ),
        help="Path to the JSON Schema file",
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
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise StateValidationError(
            [{"type": "file", "path": str(path), "message": f"{kind} not found"}]
        ) from exc
    except json.JSONDecodeError as exc:
        raise StateValidationError(
            [
                {
                    "type": "json",
                    "path": str(path),
                    "message": f"invalid JSON: {exc.msg}",
                    "line": exc.lineno,
                    "column": exc.colno,
                }
            ]
        ) from exc
    except OSError as exc:
        raise RuntimeDependencyError(f"could not read {kind}: {exc}") from exc


def json_path(error_path: Any) -> str:
    parts = [str(part) for part in error_path]
    return ".".join(parts) if parts else "$"


def validate_state(state: Any, schema: Any) -> list[dict[str, Any]]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError as exc:
        raise RuntimeDependencyError(
            "missing dependency 'jsonschema'; install with `pip install -e .[dev]`"
        ) from exc

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(state), key=lambda item: list(item.path)):
        errors.append(
            {
                "type": "schema",
                "path": json_path(error.path),
                "message": error.message,
            }
        )
    return errors


def emit_json(ok: bool, path: Path, errors: list[dict[str, Any]]) -> None:
    print(json.dumps({"ok": ok, "path": str(path), "errors": errors}, indent=2))


def emit_tty(ok: bool, path: Path, errors: list[dict[str, Any]]) -> None:
    if ok:
        print(f"valid: {path}")
        return

    print(f"invalid: {path}")
    for error in errors:
        location = error.get("path", "$")
        print(f"- {location}: {error['message']}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        schema = load_json(args.schema, "schema")
        state = load_json(args.state, "state")
        errors = validate_state(state, schema)
    except StateValidationError as exc:
        if args.format == "json":
            emit_json(False, args.state, exc.errors)
        else:
            emit_tty(False, args.state, exc.errors)
        return EXIT_USER_ERROR
    except RuntimeDependencyError as exc:
        message = str(exc)
        if args.format == "json":
            emit_json(
                False,
                args.state,
                [{"type": "runtime", "path": "$", "message": message}],
            )
        else:
            print(f"error: {message}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR

    if errors:
        if args.format == "json":
            emit_json(False, args.state, errors)
        else:
            emit_tty(False, args.state, errors)
        return EXIT_USER_ERROR

    if args.format == "json":
        emit_json(True, args.state, [])
    else:
        emit_tty(True, args.state, [])
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
