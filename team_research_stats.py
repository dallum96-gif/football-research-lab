from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from functools import lru_cache

import query_lab
from match_stats import CORE_FIELDS, OPTIONAL_FIELDS, load_csv, number

PACKAGED = Path(__file__).resolve().parent / "data" / "fixture_match_stats.csv"


def _identity_rows():
    return query_lab.load_identity_registry()


@lru_cache(maxsize=1)
def _fixture_rows():
    path = Path(__file__).resolve().parent / "fixtures_master_corrected.csv"
    return tuple(load_csv(str(path)))


@lru_cache(maxsize=1)
def _packaged_rows():
    if not PACKAGED.is_file():
        return {}
    rows = load_csv(str(PACKAGED))
    return {(r["season"], str(r["fixture_id"])): r for r in rows}


def _persistent_team(season: str, local_id: str, identity):
    for row in identity:
        if (
            row.get("season") == season
            and str(row.get("local_team_id", "")).strip() == str(local_id).strip()
            and row.get("mapping_status") == "VERIFIED"
        ):
            return str(row.get("persistent_team_code", "")).strip()
    return None


def _team_side_row(season, fixture_id, team_code, identity, fixture):
    packaged = _packaged_rows().get((season, str(fixture_id)))
    if not packaged:
        return None
    home_code = _persistent_team(season, fixture.get("home_team_id", ""), identity)
    away_code = _persistent_team(season, fixture.get("away_team_id", ""), identity)
    prefix = "home" if home_code == team_code else "away" if away_code == team_code else None
    if prefix is None:
        return None
    values = {}
    for label in CORE_FIELDS:
        key = f"{prefix}_core_{label.lower().replace(' ', '_')}"
        values[label] = number(packaged.get(key))
    for label in OPTIONAL_FIELDS:
        key = f"{prefix}_optional_{label.lower().replace(' ', '_')}"
        values[label] = number(packaged.get(key))
    return values


@lru_cache(maxsize=128)
def team_match_stats(season: str, team_code: str) -> tuple[dict, ...]:
    identity = _identity_rows()
    results = []
    for fixture in _fixture_rows():
        if fixture.get("season") != season:
            continue
        values = _team_side_row(season, fixture.get("fixture_id"), str(team_code), identity, fixture)
        if values is None:
            continue
        row = dict(values)
        row["fixture_id"] = str(fixture.get("fixture_id"))
        row["kickoff_time"] = fixture.get("kickoff_time")
        row["home"] = _persistent_team(season, fixture.get("home_team_id", ""), identity) == str(team_code)
        results.append(row)
    return tuple(results)


def team_season_stats(season: str, team_code: str) -> dict:
    rows = team_match_stats(season, team_code)
    if not rows:
        return {"status": "UNAVAILABLE", "matches": 0}

    sums = defaultdict(float)
    counts = defaultdict(int)
    for row in rows:
        for key, value in row.items():
            if key in {"fixture_id", "kickoff_time", "home"} or value is None:
                continue
            sums[key] += float(value)
            counts[key] += 1

    out = {"status": "AVAILABLE", "matches": len(rows)}
    for key, value in sums.items():
        out[key] = value
        out[f"{key}_per_match"] = value / len(rows)

    shots = out.get("Shots", 0)
    sot = out.get("Shots on target", 0)
    goals = out.get("goals_for", 0)
    xg = out.get("Expected goals")
    out["shot_accuracy"] = (sot / shots) if shots else None
    out["goals_per_shot"] = (goals / shots) if shots else None
    out["xg_overperformance"] = (goals - xg) if xg is not None else None
    out["pass_accuracy"] = (
        out.get("Accurate passes", 0) / out.get("Passes", 0)
        if out.get("Passes") else None
    )
    out["home_matches"] = sum(1 for r in rows if r["home"])
    out["away_matches"] = len(rows) - out["home_matches"]
    return out
