"""Materialise a real PulseLive fixture snapshot through the existing FRL seams.

Usage from the repository root:
    python scripts/materialize_pulselive_fixture_snapshot.py 2016-17 8

The script resolves the canonical fixture to its verified source-match ID, then
uses the established pulselive_live.snapshot() adapter to capture the real
PulseLive resources. It does not invent lineup/formation values or create a
second evidence model.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pulselive_materialization import materialize_fixture


def materialize(
    season: str,
    fixture_id: str,
    *,
    force: bool = False,
    root: Path | None = None,
) -> Path:
    result = materialize_fixture(season, fixture_id, force=force, root=root)
    print(f"{result['status']}: {season}/{fixture_id}")
    print(f"SOURCE MATCH: {result['source_match_id']}")
    print(f"SNAPSHOT: {result['snapshot_path']}")
    print(f"PLAYERS: {result['validation']['lineup_player_count']}")
    for side in ("home", "away"):
        value = result["validation"]["formation"].get(side, {})
        print(f"FORMATION {side}: {value.get('status')} / {value.get('value')}")
    return Path(result["snapshot_path"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialise one real PulseLive fixture snapshot.")
    parser.add_argument("season")
    parser.add_argument("fixture_id")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--archive-root", type=Path)
    args = parser.parse_args()
    materialize(args.season, args.fixture_id, force=args.force, root=args.archive_root)


if __name__ == "__main__":
    main()
