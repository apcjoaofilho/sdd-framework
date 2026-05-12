#!/usr/bin/env python3
"""Read configured SDD projects and emit machine-readable status JSON."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_RUNTIME_ERROR = 2


class ProjectsConfigError(Exception):
    """User-correctable projects.yaml error."""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read ~/.sdd/projects.yaml and report SDD project state."
    )
    parser.add_argument(
        "--projects-file",
        type=Path,
        default=Path.home() / ".sdd" / "projects.yaml",
        help="Path to projects.yaml",
    )
    parser.add_argument(
        "--now",
        default=None,
        help="Override current UTC time for deterministic tests",
    )
    return parser.parse_args(argv)


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"null", "~"}:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def split_key_value(line: str) -> tuple[str, Any]:
    if ":" not in line:
        raise ProjectsConfigError(f"expected key: value, got {line!r}")
    key, value = line.split(":", 1)
    key = key.strip()
    if not key:
        raise ProjectsConfigError(f"empty key in line {line!r}")
    return key, parse_scalar(value)


def parse_projects_yaml(text: str) -> list[dict[str, str]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None

    if payload is not None:
        return normalize_projects_payload(payload)

    projects: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_projects = False

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            key, value = split_key_value(stripped)
            if key != "projects":
                continue
            if value not in {"", None}:
                raise ProjectsConfigError("projects must be a list")
            in_projects = True
            continue

        if not in_projects:
            continue

        if stripped.startswith("- "):
            if current is not None:
                projects.append(current)
            current = {}
            item = stripped[2:].strip()
            if not item:
                continue
            if ":" in item:
                key, value = split_key_value(item)
                current[key] = str(value)
            else:
                current["path"] = str(parse_scalar(item))
            continue

        if current is None:
            raise ProjectsConfigError("project attributes must follow a list item")
        key, value = split_key_value(stripped)
        current[key] = str(value)

    if current is not None:
        projects.append(current)

    return normalize_projects_payload({"projects": projects})


def normalize_projects_payload(payload: Any) -> list[dict[str, str]]:
    if isinstance(payload, list):
        raw_projects = payload
    elif isinstance(payload, dict) and isinstance(payload.get("projects"), list):
        raw_projects = payload["projects"]
    else:
        raise ProjectsConfigError("projects.yaml must contain a projects list")

    projects = []
    for index, item in enumerate(raw_projects):
        if isinstance(item, str):
            item = {"path": item}
        if not isinstance(item, dict):
            raise ProjectsConfigError(f"project #{index + 1} must be a map or path")

        path = item.get("path") or item.get("root")
        if not isinstance(path, str) or not path:
            raise ProjectsConfigError(f"project #{index + 1} is missing path")

        name = item.get("name")
        if name is not None and not isinstance(name, str):
            raise ProjectsConfigError(f"project #{index + 1} name must be a string")

        projects.append({"name": name or Path(path).name, "path": path})

    return projects


def load_projects(path: Path) -> list[dict[str, str]]:
    try:
        return parse_projects_yaml(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProjectsConfigError(f"projects file not found: {path}") from exc
    except OSError as exc:
        raise ProjectsConfigError(f"could not read projects file: {exc}") from exc


def parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def lock_status(lock: Any, now: datetime) -> str:
    if not isinstance(lock, dict):
        return "unlocked"

    agent = lock.get("agent")
    if not agent or agent == "none":
        return "unlocked"

    try:
        started_at = parse_utc(str(lock["started_at"]))
        ttl_minutes = int(lock["ttl_minutes"])
    except (KeyError, TypeError, ValueError):
        return "invalid"

    expires_at = started_at + timedelta(minutes=ttl_minutes)
    if expires_at <= now:
        return "stale"
    return "locked"


def read_project_status(project: dict[str, str], now: datetime) -> dict[str, Any]:
    root = Path(project["path"]).expanduser()
    state_path = root / "STATE.json"
    base = {"name": project["name"], "path": str(root)}

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {**base, "error": "STATE.json not found"}
    except json.JSONDecodeError as exc:
        return {**base, "error": f"invalid STATE.json: {exc.msg}"}
    except OSError as exc:
        return {**base, "error": f"could not read STATE.json: {exc}"}

    return {
        **base,
        "phase": state.get("phase"),
        "branch": state.get("branch"),
        "lock_status": lock_status(state.get("lock"), now),
        "retry_count": state.get("retry_count", 0),
        "last_error": state.get("last_error"),
    }


def emit(projects: list[dict[str, Any]], errors: list[str]) -> None:
    print(
        json.dumps(
            {"ok": not errors, "projects": projects, "errors": errors},
            indent=2,
        )
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        now = parse_utc(args.now) if args.now else datetime.now(timezone.utc)
    except ValueError:
        emit([], ["--now must be an ISO 8601 timestamp"])
        return EXIT_USER_ERROR

    try:
        configured_projects = load_projects(args.projects_file)
    except ProjectsConfigError as exc:
        emit([], [str(exc)])
        return EXIT_USER_ERROR

    projects = [read_project_status(project, now) for project in configured_projects]
    emit(projects, [])
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
