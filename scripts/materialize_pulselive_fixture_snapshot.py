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
import json
import os
from pathlib import Path

from pulselive_fixture_evidence import archive_root, normalise_lineups
from pulselive_live import snapshot
from source_family_adapters import resolve_source_match


def _resource_payload(package: dict, resource: str):
    return package.get("resources", {}).get(resource, {}).get("payload")


def materialize(season: str, fixture_id: str, *, force: bool = False) -> Path:
    resolved = resolve_source_match(season, fixture_id)
    source_match_id = str(resolved["source_match_id"])

    root = archive_root()
    if root is None:
        raise RuntimeError(
            "No approved PulseLive archive root is available. Set "
            "FRL_PULSELIVE_ARCHIVE_ROOT to the approved archive directory."
        )

    target = root / f"match-{source_match_id}" / "snapshot.json"
    if target.exists() and not force:
        raise FileExistsError(
            f"Snapshot already exists: {target}. Use --force only when replacing an existing capture."
        )

    package = snapshot(source_match_id)
    lineups_payload = _resource_payload(package, "lineups")
    if lineups_payload is None:
        raise RuntimeError("PulseLive snapshot contains no lineups resource payload.")

    try:
        normalised = normalise_lineups(lineups_payload)
    except Exception as exc:
        raise RuntimeError(f"PulseLive lineup payload could not be normalised: {exc}") from exc

    players = normalised.get("players", [])
    if not players:
        raise RuntimeError("PulseLive lineup payload normalised to zero players; refusing to materialise.")

    package["frl_context"] = {
        "season": season,
        "fixture_id": str(fixture_id),
        "source_match_id": source_match_id,
        "relationship_status": resolved["relationship_status"],
    }

    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".json.tmp")
    temp.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, target)

    formations = normalised.get("formations", {})
    print(f"MATERIALISED: {season}/{fixture_id}")
    print(f"SOURCE MATCH: {source_match_id}")
    print(f"SNAPSHOT: {target}")
    print(f"PLAYERS: {len(players)}")
    for side in ("home", "away"):
        value = formations.get(side, {})
        print(f"FORMATION {side}: {value.get('status')} / {value.get('value')}")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialise one real PulseLive fixture snapshot.")
    parser.add_argument("season")
    parser.add_argument("fixture_id")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    materialize(args.season, args.fixture_id, force=args.force)


if __name__ == "__main__":
    main()
