"""Resumable, sequential PulseLive materialisation for canonical FRL fixtures.

Examples:
    python scripts/materialize_pulselive_fixture_snapshots.py \
        --archive-root data/raw/pulselive --fixture 2016-17/8

    python scripts/materialize_pulselive_fixture_snapshots.py \
        --archive-root data/raw/pulselive --retry-failures

An unfiltered universe run requires the explicit ``--all`` switch. Existing
valid snapshots are skipped by default and each outcome is recorded atomically.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pulselive_fixture_evidence import archive_root as configured_archive_root
from pulselive_materialization import (
    failed_fixture_keys,
    load_canonical_fixtures,
    load_materialization_state,
    materialize_many,
)


def _fixture_key(value: str) -> str:
    season, separator, fixture_id = value.partition("/")
    if not separator or not season.strip() or not fixture_id.strip():
        raise argparse.ArgumentTypeError("fixture must use SEASON/FIXTURE_ID, for example 2016-17/8")
    return f"{season.strip()}/{fixture_id.strip()}"


def _select_fixtures(args: argparse.Namespace, root: Path) -> list[dict[str, str]]:
    fixtures = load_canonical_fixtures(args.fixture_master)
    canonical = {f"{row['season']}/{row['fixture_id']}": row for row in fixtures}

    selected_keys: set[str] = set()
    if args.all:
        selected_keys.update(canonical)
    for season in args.season:
        selected_keys.update(key for key, row in canonical.items() if row["season"] == season)
    for key in args.fixture:
        if key not in canonical:
            raise ValueError(f"Canonical fixture does not exist: {key}")
        selected_keys.add(key)
    if args.retry_failures:
        selected_keys.update(failed_fixture_keys(load_materialization_state(root)))

    selected = [row for key, row in canonical.items() if key in selected_keys]
    if args.limit is not None:
        selected = selected[: args.limit]
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Safely materialise real PulseLive evidence for governed canonical fixtures."
    )
    parser.add_argument("--archive-root", type=Path)
    parser.add_argument("--fixture-master", type=Path, default=ROOT / "fixtures_master_corrected.csv")
    parser.add_argument("--fixture", action="append", default=[], type=_fixture_key)
    parser.add_argument("--season", action="append", default=[])
    parser.add_argument("--all", action="store_true", help="Explicitly select the complete canonical fixture universe.")
    parser.add_argument("--retry-failures", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true", help="Explicitly replace existing snapshots after validation.")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--backoff-seconds", type=float, default=2.0)
    parser.add_argument("--request-interval-seconds", type=float, default=1.0)
    parser.add_argument("--fixture-interval-seconds", type=float, default=2.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not (args.all or args.fixture or args.season or args.retry_failures):
        parser.error("select --fixture, --season, --retry-failures, or explicitly pass --all")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    if args.max_attempts < 1 or args.max_attempts > 5:
        parser.error("--max-attempts must be between 1 and 5")
    if min(args.backoff_seconds, args.request_interval_seconds, args.fixture_interval_seconds) < 0:
        parser.error("pacing and backoff values cannot be negative")

    root = args.archive_root.resolve() if args.archive_root else configured_archive_root()
    if root is None:
        parser.error("no approved archive root exists; pass --archive-root or set FRL_PULSELIVE_ARCHIVE_ROOT")
    if args.archive_root:
        root.mkdir(parents=True, exist_ok=True)
    if not root.is_dir():
        parser.error(f"archive root is not a directory: {root}")

    selected = _select_fixtures(args, root)
    if not selected:
        print("No canonical fixtures matched the requested selection.")
        return
    if args.dry_run:
        print(json.dumps({"archive_root": str(root), "selected": selected}, indent=2))
        return

    result = materialize_many(
        selected,
        root=root,
        force=args.force,
        timeout=args.timeout,
        max_attempts=args.max_attempts,
        backoff_seconds=args.backoff_seconds,
        request_interval_seconds=args.request_interval_seconds,
        fixture_interval_seconds=args.fixture_interval_seconds,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["counts"]["FAILED"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
