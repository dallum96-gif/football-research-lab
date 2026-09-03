from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pulselive_fixture_evidence


PASSING_TOKENS = (
    "pass",
    "cross",
    "through",
    "assist",
    "chance",
    "possession",
)


def _normalise_path(path: str) -> str:
    return path.replace(".[].", "[].").replace(".[]", "[]")


def _key_paths(value: Any, prefix: str = "") -> set[str]:
    paths: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            paths.add(child_prefix)
            paths.update(_key_paths(child, child_prefix))
    elif isinstance(value, list):
        child_prefix = f"{prefix}[]" if prefix else "[]"
        for child in value[:5]:
            paths.update(_key_paths(child, child_prefix))
    return {_normalise_path(path) for path in paths}


def _passing_paths(value: Any) -> list[str]:
    matches = {
        path
        for path in _key_paths(value)
        if any(token in path.casefold() for token in PASSING_TOKENS)
    }
    return sorted(matches, key=str.casefold)


def discover_snapshot(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        snapshot = json.load(handle)
    if not isinstance(snapshot, dict):
        raise ValueError(f"PulseLive snapshot must be a JSON object: {path}")

    resources = snapshot.get("resources")
    if not isinstance(resources, dict):
        resources = {}

    resource_matches: dict[str, list[str]] = {}
    for name, resource in resources.items():
        payload = (
            resource.get("payload")
            if isinstance(resource, dict) and "payload" in resource
            else resource
        )
        matches = _passing_paths(payload)
        if matches:
            resource_matches[str(name)] = matches

    fixture_context = snapshot.get("fixture")
    if not isinstance(fixture_context, dict):
        fixture_context = {}

    return {
        "path": str(path),
        "source_match_id": (
            fixture_context.get("id")
            or fixture_context.get("matchId")
            or snapshot.get("source_match_id")
        ),
        "resource_count": len(resources),
        "passing_resources": resource_matches,
        "passing_path_count": sum(len(paths) for paths in resource_matches.values()),
    }


def _snapshot_paths(root: Path) -> list[Path]:
    canonical = sorted(root.rglob("snapshot.json"))
    if canonical:
        return canonical
    return sorted(
        path
        for path in root.rglob("*.json")
        if path.is_file() and path.name not in {"manifest.json", "source_manifest.json"}
    )


def audit_archive(root: Path, *, limit: int | None = None) -> dict[str, Any]:
    paths = _snapshot_paths(root)
    if limit is not None:
        paths = paths[:limit]

    snapshots: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    all_resource_names: set[str] = set()
    all_passing_paths: set[str] = set()

    for path in paths:
        try:
            result = discover_snapshot(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append({"path": str(path), "error": str(exc)})
            continue
        snapshots.append(result)
        all_resource_names.update(result["passing_resources"].keys())
        for matches in result["passing_resources"].values():
            all_passing_paths.update(matches)

    snapshots_with_passing = [
        result for result in snapshots if result["passing_path_count"] > 0
    ]

    return {
        "archive_root": str(root),
        "snapshot_files_scanned": len(paths),
        "snapshots_read": len(snapshots),
        "snapshots_with_passing_fields": len(snapshots_with_passing),
        "passing_resource_names": sorted(all_resource_names, key=str.casefold),
        "passing_key_paths": sorted(all_passing_paths, key=str.casefold),
        "snapshots": snapshots_with_passing,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read preserved PulseLive snapshots and report pass/cross/through-ball/"
            "chance/possession-like key paths without altering source evidence."
        )
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        help="Explicit PulseLive archive root. Defaults to FRL archive discovery.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of snapshot files to inspect.",
    )
    args = parser.parse_args()

    root = args.archive_root.expanduser().resolve() if args.archive_root else pulselive_fixture_evidence.archive_root()
    if root is None or not root.is_dir():
        raise SystemExit(
            "No PulseLive archive root was found. Set FRL_PULSELIVE_ARCHIVE_ROOT "
            "or pass --archive-root."
        )
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be at least 1 when supplied.")

    print(json.dumps(audit_archive(root, limit=args.limit), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
