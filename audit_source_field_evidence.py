"""Evidence audit for every currently uncatalogued source field.

Reads the user's local Premier-League-Stats source archive and reports source-level
schema/value evidence without promoting or modifying any field.
"""
from __future__ import annotations

from pathlib import Path
import math
import pandas as pd

from source_field_review_queue import build_review_queue

DEFAULT_ROOT = Path(r"C:\Users\dlall\football_database\Premier-League-Stats\pl_stats")


def _candidate_files(root: Path, family: str, season: str) -> list[Path]:
    if family == "team_match":
        pattern = f"**/{season}_events_stats.csv"
        return sorted(root.glob(pattern))
    if family == "player_match":
        pattern = f"**/{season}_players_match_stats.csv"
        return sorted(root.glob(pattern))
    if family == "player_season":
        pattern = f"**/{season}_players_stats.csv"
        return sorted(root.glob(pattern))
    if family == "squad":
        pattern = f"**/{season}_squad.csv"
        return sorted(root.glob(pattern))
    return []


def _safe_number(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def _summarise(series: pd.Series) -> dict:
    s = series.dropna()
    out = {
        "rows": int(series.shape[0]),
        "non_null": int(series.notna().sum()),
        "null_pct": round(float(series.isna().mean() * 100), 2),
        "dtype": str(series.dtype),
        "distinct": int(s.nunique(dropna=True)),
    }
    if s.empty:
        out.update({"minimum": None, "maximum": None, "examples": []})
        return out
    numeric = pd.to_numeric(s, errors="coerce")
    if numeric.notna().all():
        out["minimum"] = _safe_number(numeric.min())
        out["maximum"] = _safe_number(numeric.max())
    else:
        out["minimum"] = None
        out["maximum"] = None
    out["examples"] = [str(x) for x in s.astype(str).drop_duplicates().head(5).tolist()]
    return out


def run(root: Path = DEFAULT_ROOT) -> list[dict]:
    queue = build_review_queue()
    rows: list[dict] = []
    for item in queue:
        field = item["source_field"]
        family = item["family"]
        seasons = item.get("seasons_present", 0)
        season_span = item.get("season_start")
        # Inspect a representative file for each covered season, capped at one file
        # per season to avoid multiplying club-level files unnecessarily.
        evidence = []
        inspected = set()
        for season in item.get("seasons", ()):  # catalog supplies observed seasons
            files = _candidate_files(root, family, season)
            chosen = next((p for p in files if p not in inspected), None)
            if chosen is None:
                continue
            inspected.add(chosen)
            try:
                header = pd.read_csv(chosen, nrows=0)
            except Exception as exc:  # pragma: no cover - environment-dependent
                evidence.append({"season": season, "file": str(chosen), "error": str(exc)})
                continue
            if field not in header.columns:
                continue
            try:
                data = pd.read_csv(chosen, usecols=[field])
                summary = _summarise(data[field])
                evidence.append({"season": season, "file": str(chosen), **summary})
            except Exception as exc:  # pragma: no cover - environment-dependent
                evidence.append({"season": season, "file": str(chosen), "error": str(exc)})
        rows.append({
            "family": family,
            "source_field": field,
            "coverage_class": item["coverage_class"],
            "seasons_present": seasons,
            "season_start": season_span,
            "evidence": evidence,
        })
    return rows


def print_report(rows: list[dict]) -> None:
    print("=" * 120)
    print("FRL SOURCE-FIELD VALUE EVIDENCE AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 120)
    print(f"Fields inspected: {len(rows)}")
    print()
    for row in rows:
        print(f"{row['family']:14} | {row['source_field']:45} | {row['coverage_class']:14} | seasons={row['seasons_present']}")
        for ev in row["evidence"][:3]:
            if "error" in ev:
                print(f"  {ev['season']} | ERROR | {ev['error']}")
            else:
                print(
                    f"  {ev['season']} | dtype={ev['dtype']:<12} non_null={ev['non_null']}/{ev['rows']} "
                    f"distinct={ev['distinct']} range=({ev['minimum']},{ev['maximum']}) "
                    f"examples={ev['examples']}"
                )
        if len(row["evidence"]) > 3:
            print(f"  ... {len(row['evidence']) - 3} additional season samples")
    print("\nIMPORTANT")
    print("- This is source evidence only; it does not promote or canonicalise any field.")
    print("- Representative values are evidence about population/type/range, not a semantic definition by themselves.")
    print("=" * 120)


if __name__ == "__main__":
    print_report(run())
