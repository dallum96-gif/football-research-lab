"""Read-only audit of the early-season FPL -> PL player source bridge.

Purpose: test whether the repository's _merged/players season files provide a
source-local bridge for 2016-20 FPL identities before any canonical identity
promotion is attempted.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
import unicodedata

import player_research
from player_identity_crosswalk import SEASONS
from source_family_adapters import player_season_source_rows

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "data" / "_source_probe_placeholder"  # replaced at runtime


def normalize_name(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def locate_root() -> Path:
    candidates = [
        ROOT.parent / "Premier-League-Stats" / "pl_stats",
        Path(r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats"),
    ]
    for path in candidates:
        if path.is_dir():
            return path
    raise FileNotFoundError("Premier-League-Stats/pl_stats source root not found")


def load_csv(path: Path):
    import csv
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise ValueError(path)


def merged_player_rows(season: str):
    root = locate_root()
    path = root / "_merged" / "players" / f"{season}_players_stats.csv"
    if not path.is_file():
        return (), path
    return tuple(load_csv(path)), path


def audit(seasons=("2016-17", "2017-18", "2018-19", "2019-20")):
    report = {"seasons": {}, "total": defaultdict(int)}
    for season in seasons:
        fpl = {}
        for row in player_research._load_season_rows(season):
            element = str(row.get("element") or row.get("player_code") or "").strip()
            if element:
                fpl.setdefault((season, element), row)

        merged, path = merged_player_rows(season)
        by_name = defaultdict(set)
        by_name_rows = defaultdict(list)
        for row in merged:
            pid = str(row.get("playerId") or row.get("playerid") or "").strip()
            name = normalize_name(row.get("playerName") or row.get("playername"))
            if pid and name:
                by_name[(season, name)].add(pid)
                by_name_rows[(season, name)].append(row)

        ps_ids = {
            str(r.get("playerId") or "").strip()
            for r in player_season_source_rows(season)
            if str(r.get("playerId") or "").strip()
        }

        rows = []
        for (s, element), r in fpl.items():
            name = player_research.display_player_name(r)
            cands = sorted(by_name.get((season, normalize_name(name)), set()))
            if not cands:
                status = "NO_MERGED_NAME_CANDIDATE"
            elif len(cands) > 1:
                status = "AMBIGUOUS_MERGED_NAME"
            else:
                pid = cands[0]
                status = "MERGED_MATCH" if pid in ps_ids else "MERGED_MATCH_NO_PLAYER_SEASON"
            rows.append((element, name, cands, status))

        counts = defaultdict(int)
        for _, _, _, status in rows:
            counts[status] += 1
        report["seasons"][season] = {
            "fpl_identities": len(fpl),
            "merged_rows": len(merged),
            "merged_file": str(path),
            **counts,
        }
        for k, v in counts.items():
            report["total"][k] += v

    return report


def print_report(report):
    print("=" * 96)
    print("FRL EARLY-SEASON FPL -> PL PLAYER SOURCE BRIDGE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 96)
    for season, info in report["seasons"].items():
        print(f"{season}: FPL={info['fpl_identities']:,} | merged-player rows={info['merged_rows']:,}")
        print(f"  MERGED_MATCH={info.get('MERGED_MATCH',0):,} | MERGED_MATCH_NO_PLAYER_SEASON={info.get('MERGED_MATCH_NO_PLAYER_SEASON',0):,} | NO_NAME={info.get('NO_MERGED_NAME_CANDIDATE',0):,} | AMBIGUOUS={info.get('AMBIGUOUS_MERGED_NAME',0):,}")
        print(f"  source={info['merged_file']}")
    print("\nTOTALS:")
    for k, v in sorted(report["total"].items()):
        print(f"  {k}: {v:,}")
    print("\nNo files were written or modified.")
    print("=" * 96)


if __name__ == "__main__":
    print_report(audit())
