"""Read-only audit of players_match_stats playerId longitudinal identity."""

from __future__ import annotations

import csv
import unicodedata
from collections import defaultdict
from pathlib import Path

PL_ROOT = Path(r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats")
SEASONS = (
    "2016-17", "2017-18", "2018-19", "2019-20", "2020-21",
    "2021-22", "2022-23", "2023-24", "2024-25", "2025-26",
)


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.casefold().split())


def open_csv(path: Path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            handle = path.open("r", encoding=encoding, newline="")
            return handle, csv.DictReader(handle)
        except UnicodeDecodeError:
            try:
                handle.close()
            except Exception:
                pass
    raise ValueError(f"Could not decode {path}")


def source_files(season: str):
    target = f"{season}_players_match_stats.csv"
    return tuple(sorted(PL_ROOT.rglob(target)))


def audit() -> dict:
    by_source = defaultdict(lambda: {
        "seasons": set(),
        "names": set(),
        "teams": set(),
        "rows": 0,
    })

    seasonal_counts = {}

    for season in SEASONS:
        rows = 0
        ids = set()
        for path in source_files(season):
            handle, reader = open_csv(path)
            for row in reader:
                pid = str(
                    row.get("playerId")
                    or row.get("player_id")
                    or ""
                ).strip()
                if not pid:
                    continue
                rows += 1
                ids.add(pid)
                rec = by_source[pid]
                rec["seasons"].add(season)
                rec["names"].add(normalize_name(
                    row.get("playerName") or row.get("player_name") or ""
                ))
                team = str(row.get("team_id") or "").strip()
                if team:
                    rec["teams"].add(team)
                rec["rows"] += 1
            handle.close()
        seasonal_counts[season] = {"rows": rows, "unique_player_ids": len(ids)}

    multi_season = {
        pid: rec for pid, rec in by_source.items() if len(rec["seasons"]) > 1
    }
    multi_names = {
        pid: rec for pid, rec in by_source.items() if len(rec["names"]) > 1
    }

    conflicts = {
        pid: rec for pid, rec in by_source.items()
        if any(name == "" for name in rec["names"]) or len(rec["names"]) > 1
    }

    return {
        "seasonal_counts": seasonal_counts,
        "unique_source_players": len(by_source),
        "multi_season_ids": multi_season,
        "multi_name_ids": multi_names,
        "conflict_ids": conflicts,
        "source_players": by_source,
    }


def print_report(report: dict) -> None:
    print("=" * 96)
    print("FRL / PLAYER-MATCH SOURCE PLAYER-ID LONGITUDINAL IDENTITY AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    print()

    for season, data in report["seasonal_counts"].items():
        print(
            f"{season}: rows={data['rows']:,} "
            f"unique playerIds={data['unique_player_ids']:,}"
        )

    print()
    print(f"Unique source playerIds:           {report['unique_source_players']:,}")
    print(f"playerIds spanning >1 season:      {len(report['multi_season_ids']):,}")
    print(f"playerIds with >1 normalized name: {len(report['multi_name_ids']):,}")
    print(f"playerIds with identity conflicts: {len(report['conflict_ids']):,}")
    print()

    if report["multi_name_ids"]:
        print("MULTI-NAME SAMPLE:")
        for pid, rec in list(sorted(report["multi_name_ids"].items()))[:25]:
            print(
                f"  source={pid} | seasons={sorted(rec['seasons'])} "
                f"| names={sorted(rec['names'])} | teams={sorted(rec['teams'])}"
            )
        print()

    print("No files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(audit())
