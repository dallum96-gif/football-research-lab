"""Materialise the governed rich player-season Product projection.

The preserved provider folders are read only here. Runtime Player Stats reads
``data/rich_player_season_stats.csv`` and therefore does not depend on the raw
provider checkout being present.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_match_stats  # noqa: E402
import rich_player_projection  # noqa: E402


CORE_SEASONS = (
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
)
DEFAULT_OUTPUT = ROOT / "data" / "rich_player_season_stats.csv"


def _fieldnames() -> list[str]:
    return ["season", "player_code", "source_player_id", *rich_player_projection.RICH_PLAYER_METRICS]


def _read_existing(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _materialize_season(season: str) -> list[dict[str, object]]:
    fields = set(player_match_stats.source_fields(season))
    bridge = player_match_stats.pulselive_player_bridge_index(season)
    rows: list[dict[str, object]] = []

    for player_code, identity in sorted(bridge.items(), key=lambda item: item[0]):
        source_player_id = str(identity.get("player_id") or "").strip()
        if not source_player_id:
            continue
        records = player_match_stats.player_match_records_for_player(source_player_id, season)
        if not records:
            continue
        totals = rich_player_projection.aggregate_source_records(records, fields)
        rows.append(
            {
                "season": season,
                "player_code": str(player_code),
                "source_player_id": source_player_id,
                **totals,
            }
        )
    if not rows:
        raise RuntimeError(f"No governed player-season projection rows materialised for {season}")
    return rows


def materialize(pl_root: Path, seasons: tuple[str, ...], output: Path) -> dict[str, int]:
    if not pl_root.is_dir():
        raise RuntimeError(f"Preserved Premier-League-Stats root not found: {pl_root}")

    player_match_stats.PL_ROOT = pl_root
    player_match_stats._season_player_match_files.cache_clear()
    player_match_stats.source_fields.cache_clear()
    player_match_stats._source_match_records.cache_clear()
    player_match_stats._player_match_pair_index.cache_clear()
    player_match_stats._player_match_rows_by_match.cache_clear()
    player_match_stats.pulselive_player_bridge_index.cache_clear()

    generated = [row for season in seasons for row in _materialize_season(season)]
    selected = set(seasons)
    preserved = [
        row
        for row in _read_existing(output)
        if str(row.get("season") or "").strip() not in selected
    ]
    rows = preserved + generated
    season_order = {season: index for index, season in enumerate((*CORE_SEASONS, "2026-27"))}
    rows.sort(
        key=lambda row: (
            season_order.get(str(row.get("season") or ""), 999),
            str(row.get("player_code") or ""),
        )
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_fieldnames(), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return {
        season: sum(str(row.get("season") or "") == season for row in generated)
        for season in seasons
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument(
        "--season",
        action="append",
        dest="seasons",
        choices=CORE_SEASONS,
        help="Season to rebuild; repeat as needed. Defaults to the core decade.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    seasons = tuple(args.seasons or CORE_SEASONS)
    counts = materialize(args.pl_root, seasons, args.output)
    print("FRL RICH PLAYER-SEASON MATERIALIZATION")
    for season in seasons:
        print(f"{season}: {counts[season]} players")
    print(f"output={args.output}")
    print(f"metrics={len(rich_player_projection.RICH_PLAYER_METRICS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
