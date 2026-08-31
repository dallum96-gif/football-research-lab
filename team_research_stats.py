from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import query_lab
from match_stats import CORE_FIELDS, OPTIONAL_FIELDS, load_csv, number
from team_metric_missingness import (
    normalise_team_match_observation,
    team_match_missingness_semantics,
)

PACKAGED = Path(__file__).resolve().parent / "data" / "fixture_match_stats.csv"
FIXTURES = Path(__file__).resolve().parent / "fixtures_master_corrected.csv"


def _identity_rows():
    return query_lab.load_identity_registry()


@lru_cache(maxsize=1)
def _fixture_rows():
    return tuple(load_csv(str(FIXTURES)))


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


def team_code_for_name(season: str, team: str) -> str | None:
    for row in _identity_rows():
        if (
            row.get("season") == season
            and row.get("mapping_status") == "VERIFIED"
            and str(row.get("canonical_name", "")).replace("_", " ").casefold() == str(team).casefold()
        ):
            return str(row.get("persistent_team_code", "")).strip()
    return None


def _team_side_row(season, fixture_id, team_code, identity, fixture):
    packaged = _packaged_rows().get((season, str(fixture_id)))
    home_code = _persistent_team(season, fixture.get("home_team_id", ""), identity)
    away_code = _persistent_team(season, fixture.get("away_team_id", ""), identity)
    prefix = "home" if home_code == team_code else "away" if away_code == team_code else None
    if prefix is None:
        return None

    # Canonical completed-result evidence is independently usable when the
    # optional packaged team-match representation is absent.  Scheduled rows
    # remain outside completed-match aggregation, and every unavailable
    # team-match metric remains missing rather than becoming zero.
    home_score = number(fixture.get("home_score"))
    away_score = number(fixture.get("away_score"))
    if home_score is None or away_score is None:
        return None

    values = {}
    for label in CORE_FIELDS:
        key = f"{prefix}_core_{label.lower().replace(' ', '_')}"
        values[label] = number(packaged.get(key)) if packaged else None
    for label in OPTIONAL_FIELDS:
        key = f"{prefix}_optional_{label.lower().replace(' ', '_')}"
        values[label] = number(packaged.get(key)) if packaged else None

    if prefix == "home":
        values["goals_for"] = home_score
        values["goals_against"] = away_score
    else:
        values["goals_for"] = away_score
        values["goals_against"] = home_score

    return values, prefix == "home"


@lru_cache(maxsize=128)
def team_match_stats(season: str, team_code: str) -> tuple[dict, ...]:
    identity = _identity_rows()
    results = []
    for fixture in _fixture_rows():
        if fixture.get("season") != season:
            continue
        selected = _team_side_row(season, fixture.get("fixture_id"), str(team_code), identity, fixture)
        if selected is None:
            continue
        values, is_home = selected
        row = {}
        structural_zero_fields = []
        for key, raw_value in values.items():
            value, structural_zero = normalise_team_match_observation(
                season,
                key,
                raw_value,
            )
            row[key] = value
            if structural_zero:
                structural_zero_fields.append(key)
        row["fixture_id"] = str(fixture.get("fixture_id"))
        row["kickoff_time"] = fixture.get("kickoff_time")
        row["home"] = is_home
        row["_structural_zero_fields"] = tuple(structural_zero_fields)
        results.append(row)
    return tuple(results)


def team_season_stats(season: str, team_code: str) -> dict:
    rows = team_match_stats(season, team_code)
    if not rows:
        return {"status": "UNAVAILABLE", "matches": 0}

    eligible_matches = len(rows)
    context_fields = {
        "fixture_id",
        "kickoff_time",
        "home",
        "_structural_zero_fields",
    }
    metric_fields = sorted(
        {
            key
            for row in rows
            for key in row
            if key not in context_fields and not key.startswith("_")
        }
    )
    sums = defaultdict(float)
    observed_rows: dict[str, set[int]] = {
        key: set() for key in metric_fields
    }
    source_observed_rows: dict[str, set[int]] = {
        key: set() for key in metric_fields
    }
    structural_zero_rows: dict[str, set[int]] = {
        key: set() for key in metric_fields
    }

    for index, row in enumerate(rows):
        row_structural_zeros = set(row.get("_structural_zero_fields", ()))
        for key in metric_fields:
            value = row.get(key)
            inferred_value, inferred_structural_zero = normalise_team_match_observation(
                season,
                key,
                value,
            )
            if inferred_value is None:
                continue

            is_structural_zero = (
                inferred_structural_zero
                or key in row_structural_zeros
            )
            sums[key] += float(inferred_value)
            observed_rows[key].add(index)
            if is_structural_zero:
                structural_zero_rows[key].add(index)
            else:
                source_observed_rows[key].add(index)

    out = {
        "status": "AVAILABLE",
        "matches": eligible_matches,
        "metric_coverage": {},
    }
    for key in metric_fields:
        observed_matches = len(observed_rows[key])
        source_observed_matches = len(source_observed_rows[key])
        structural_zero_matches = len(structural_zero_rows[key])
        missing_matches = eligible_matches - observed_matches
        observed_total = sums[key] if observed_matches else None
        per_observed_match = (
            observed_total / observed_matches
            if observed_total is not None
            else None
        )
        coverage_status = (
            "COMPLETE"
            if observed_matches == eligible_matches
            else "PARTIAL"
            if observed_matches
            else "UNAVAILABLE"
        )

        out["metric_coverage"][key] = {
            "eligible_matches": eligible_matches,
            "source_observed_matches": source_observed_matches,
            "structural_zero_matches": structural_zero_matches,
            "observed_matches": observed_matches,
            "missing_matches": missing_matches,
            "observed_total": observed_total,
            "per_observed_match": per_observed_match,
            "missingness_semantics": team_match_missingness_semantics(
                season,
                key,
            ),
            "coverage_complete": observed_matches == eligible_matches,
            "coverage_status": coverage_status,
        }

        if observed_total is not None:
            # Compatibility aliases: totals retain their established keys,
            # while per-match values use the governed observed population.
            out[key] = observed_total
            out[f"{key}_per_match"] = per_observed_match

    score_rows = [
        row
        for row in rows
        if row.get("goals_for") is not None
        and row.get("goals_against") is not None
    ]
    result_observed_matches = len(score_rows)
    out["result_coverage"] = {
        "eligible_matches": eligible_matches,
        "observed_matches": result_observed_matches,
        "missing_matches": eligible_matches - result_observed_matches,
        "coverage_complete": result_observed_matches == eligible_matches,
        "coverage_status": (
            "COMPLETE"
            if result_observed_matches == eligible_matches
            else "PARTIAL"
            if result_observed_matches
            else "UNAVAILABLE"
        ),
    }

    wins = sum(1 for row in score_rows if row["goals_for"] > row["goals_against"])
    draws = sum(1 for row in score_rows if row["goals_for"] == row["goals_against"])
    losses = sum(1 for row in score_rows if row["goals_for"] < row["goals_against"])
    clean_sheets = sum(1 for row in score_rows if row["goals_against"] == 0)
    failed_to_score = sum(1 for row in score_rows if row["goals_for"] == 0)

    out["wins"] = wins
    out["draws"] = draws
    out["losses"] = losses
    out["win_rate"] = (
        wins / result_observed_matches
        if result_observed_matches
        else None
    )
    out["points"] = wins * 3 + draws
    out["points_per_match"] = (
        out["points"] / result_observed_matches
        if result_observed_matches
        else None
    )
    score_population_comparable = (
        observed_rows.get("goals_for")
        == observed_rows.get("goals_against")
        and bool(observed_rows.get("goals_for"))
    )
    out["goal_difference"] = (
        out["goals_for"] - out["goals_against"]
        if score_population_comparable
        else None
    )
    out["clean_sheets"] = clean_sheets
    out["clean_sheet_rate"] = (
        clean_sheets / result_observed_matches
        if result_observed_matches
        else None
    )
    out["failed_to_score_rate"] = (
        failed_to_score / result_observed_matches
        if result_observed_matches
        else None
    )

    def comparable_population(*keys: str, complete: bool = False) -> bool:
        populations = [observed_rows.get(key, set()) for key in keys]
        if not populations or not populations[0]:
            return False
        if any(population != populations[0] for population in populations[1:]):
            return False
        return not complete or len(populations[0]) == eligible_matches

    shots = out.get("Shots", 0)
    sot = out.get("Shots on target", 0)
    goals = out.get("goals_for", 0)
    xg = out.get("Expected goals")
    out["shot_accuracy"] = (
        sot / shots
        if shots
        and comparable_population("Shots on target", "Shots")
        else None
    )
    out["goals_per_shot"] = (
        goals / shots
        if shots
        and comparable_population("goals_for", "Shots")
        else None
    )
    out["xg_overperformance"] = (
        goals - xg
        if xg is not None
        and comparable_population(
            "goals_for",
            "Expected goals",
            complete=True,
        )
        else None
    )
    out["pass_accuracy"] = (
        out.get("Accurate passes", 0) / out.get("Passes", 0)
        if out.get("Passes")
        and comparable_population("Accurate passes", "Passes")
        else None
    )
    out["home_matches"] = sum(1 for r in rows if r["home"])
    out["away_matches"] = eligible_matches - out["home_matches"]
    return out


def team_season_stats_by_name(season: str, team: str) -> dict:
    code = team_code_for_name(season, team)
    if code is None:
        return {"status": "UNAVAILABLE", "matches": 0}
    return team_season_stats(season, code)
