from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Iterable

import query_lab
import team_research_stats
from expected_metric_artifact import team_expected_metric_observation
from expected_metric_routing import EXPECTED_GOALS, PLAYER_MATCH_DERIVED_TEAM_MATCH


STATE_VERSION = "team-state-v1"
DEFAULT_RECENT_WINDOWS = (5, 10)
DIRECT_TEAM_MATCH = "DIRECT_TEAM_MATCH"
CANONICAL_FIXTURE_RESULT = "CANONICAL_FIXTURE_RESULT"


@dataclass(frozen=True)
class StateMetric:
    key: str
    label: str
    unit: str
    source_key: str | None
    opponent_source_key: str | None
    representation: str


# V1 deliberately starts with a compact, interpretable state vector. FRL owns
# far more data; extra model features should earn inclusion empirically.
STATE_METRICS = (
    StateMetric("goals_for", "Goals for", "goals", "goals_for", None, CANONICAL_FIXTURE_RESULT),
    StateMetric("goals_against", "Goals against", "goals", "goals_against", None, CANONICAL_FIXTURE_RESULT),
    StateMetric("shots_for", "Shots for", "shots", "Shots", None, DIRECT_TEAM_MATCH),
    StateMetric("shots_against", "Shots against", "shots", None, "Shots", DIRECT_TEAM_MATCH),
    StateMetric("shots_on_target_for", "Shots on target for", "shots", "Shots on target", None, DIRECT_TEAM_MATCH),
    StateMetric("shots_on_target_against", "Shots on target against", "shots", None, "Shots on target", DIRECT_TEAM_MATCH),
    StateMetric("xg_for", "Expected goals for", "xG", None, None, PLAYER_MATCH_DERIVED_TEAM_MATCH),
    StateMetric("xg_against", "Expected goals against", "xG", None, None, PLAYER_MATCH_DERIVED_TEAM_MATCH),
    StateMetric("penalty_area_entries_for", "Penalty-area entries", "entries", "Penalty area entries", None, DIRECT_TEAM_MATCH),
    StateMetric("penalty_area_entries_against", "Penalty-area entries against", "entries", None, "Penalty area entries", DIRECT_TEAM_MATCH),
    StateMetric("touches_in_box_for", "Touches in opposition box", "touches", "Touches in opposition box", None, DIRECT_TEAM_MATCH),
    StateMetric("touches_in_box_against", "Touches conceded in box", "touches", None, "Touches in opposition box", DIRECT_TEAM_MATCH),
    StateMetric("final_third_entries_for", "Final-third entries", "entries", "Final third entries", None, DIRECT_TEAM_MATCH),
    StateMetric("final_third_entries_against", "Final-third entries against", "entries", None, "Final third entries", DIRECT_TEAM_MATCH),
    StateMetric("possession", "Possession", "%", "Possession", None, DIRECT_TEAM_MATCH),
    StateMetric(
        "possessions_won_attacking_third",
        "Possessions won in attacking third",
        "events",
        "Possession won attacking third",
        None,
        DIRECT_TEAM_MATCH,
    ),
)


def _dt(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _completed(row: dict) -> bool:
    return _number(row.get("home_score")) is not None and _number(row.get("away_score")) is not None


@lru_cache(maxsize=1)
def _identity_index() -> dict[tuple[str, str], dict]:
    output: dict[tuple[str, str], dict] = {}
    for row in query_lab.load_identity_registry():
        if str(row.get("mapping_status") or "") != "VERIFIED":
            continue
        season = str(row.get("season") or "").strip()
        local_id = str(row.get("local_team_id") or "").strip()
        code = str(row.get("persistent_team_code") or "").strip()
        if season and local_id and code:
            output[(season, local_id)] = {
                "persistent_team_code": code,
                "display_name": str(row.get("canonical_name") or "").replace("_", " ").strip(),
            }
    return output


def _identity(season: str, local_id: object) -> dict | None:
    return _identity_index().get((str(season), str(local_id)))


@lru_cache(maxsize=256)
def _team_stats_index(season: str, team_code: str) -> dict[str, dict]:
    return {
        str(row.get("fixture_id") or ""): dict(row)
        for row in team_research_stats.team_match_stats(season, team_code)
    }


def _fixture_side_for_team(fixture: dict, team_code: str) -> tuple[str, dict] | None:
    season = str(fixture.get("season") or "")
    home = _identity(season, fixture.get("home_team_id"))
    away = _identity(season, fixture.get("away_team_id"))
    if home and home["persistent_team_code"] == team_code:
        return "home", away or {}
    if away and away["persistent_team_code"] == team_code:
        return "away", home or {}
    return None


def _team_code_for_side(fixture: dict, side: str) -> str:
    season = str(fixture.get("season") or "")
    identity = _identity(season, fixture.get(f"{side}_team_id"))
    if identity is None:
        raise ValueError(f"No verified {side} team identity for {season}/{fixture.get('fixture_id')}.")
    return str(identity["persistent_team_code"])


def _previous_season(season: str) -> str | None:
    try:
        start = int(str(season).split("-", 1)[0])
    except (TypeError, ValueError):
        return None
    return f"{start - 1}-{str(start)[-2:]}"


def _result_points(fixture: dict, side: str) -> tuple[str, int]:
    home = float(fixture["home_score"])
    away = float(fixture["away_score"])
    goals_for, goals_against = (home, away) if side == "home" else (away, home)
    if goals_for > goals_against:
        return "W", 3
    if goals_for < goals_against:
        return "L", 0
    return "D", 1


def _expected_goals(season: str, fixture_id: str, side: str) -> tuple[float | None, str | None, str]:
    try:
        observation = team_expected_metric_observation(season, fixture_id, side, EXPECTED_GOALS)
    except (FileNotFoundError, RuntimeError, ValueError):
        return None, None, "UNAVAILABLE"
    value = _number(observation.get("value"))
    status = str(observation.get("status") or "UNAVAILABLE")
    representation = (
        str(observation.get("representation") or "") or None
        if value is not None and status == "AVAILABLE"
        else None
    )
    return value, representation, status


@lru_cache(maxsize=1)
def _result_history() -> dict[str, tuple[tuple[datetime, int], ...]]:
    history: dict[str, list[tuple[datetime, int]]] = {}
    for fixture in query_lab.load_fixtures():
        kickoff = _dt(fixture.get("kickoff_time"))
        if kickoff is None or not _completed(fixture):
            continue
        season = str(fixture.get("season") or "")
        for side in ("home", "away"):
            identity = _identity(season, fixture.get(f"{side}_team_id"))
            if identity is None:
                continue
            _result, points = _result_points(fixture, side)
            history.setdefault(str(identity["persistent_team_code"]), []).append((kickoff, points))
    return {code: tuple(sorted(rows, key=lambda item: item[0])) for code, rows in history.items()}


def _prior_result_ppg(team_code: str, cutoff: datetime) -> tuple[float | None, int]:
    prior = [points for kickoff, points in _result_history().get(team_code, ()) if kickoff < cutoff]
    return ((sum(prior) / len(prior)) if prior else None, len(prior))


def _observation_for_fixture(fixture: dict, team_code: str) -> dict | None:
    if not _completed(fixture):
        return None
    side_context = _fixture_side_for_team(fixture, team_code)
    if side_context is None:
        return None
    side, opponent_identity = side_context
    opponent_code = str(opponent_identity.get("persistent_team_code") or "")
    season = str(fixture.get("season") or "")
    fixture_id = str(fixture.get("fixture_id") or "")
    kickoff = _dt(fixture.get("kickoff_time"))
    if not opponent_code or kickoff is None:
        return None

    own = _team_stats_index(season, team_code).get(fixture_id, {})
    opponent = _team_stats_index(season, opponent_code).get(fixture_id, {})
    result, points = _result_points(fixture, side)
    xg_for, xg_representation, xg_for_status = _expected_goals(season, fixture_id, side)
    opponent_side = "away" if side == "home" else "home"
    xg_against, xg_against_representation, xg_against_status = _expected_goals(
        season, fixture_id, opponent_side
    )

    values: dict[str, float | None] = {}
    for spec in STATE_METRICS:
        if spec.key == "xg_for":
            values[spec.key] = xg_for
        elif spec.key == "xg_against":
            values[spec.key] = xg_against
        elif spec.source_key is not None:
            values[spec.key] = _number(own.get(spec.source_key))
        elif spec.opponent_source_key is not None:
            values[spec.key] = _number(opponent.get(spec.opponent_source_key))
        else:
            values[spec.key] = None

    opponent_ppg, opponent_prior_matches = _prior_result_ppg(opponent_code, kickoff)
    return {
        "season": season,
        "fixture_id": fixture_id,
        "kickoff_time": fixture.get("kickoff_time"),
        "venue": side,
        "opponent_team_code": opponent_code,
        "opponent_name": opponent_identity.get("display_name"),
        "result": result,
        "points": points,
        "opponent_pre_match_ppg": opponent_ppg,
        "opponent_pre_match_matches": opponent_prior_matches,
        "state_metrics": values,
        "representations": {
            "expected_goals_for": xg_representation,
            "expected_goals_against": xg_against_representation,
        },
        "expected_goal_status": {"for": xg_for_status, "against": xg_against_status},
    }


def _preceding_observations(target_fixture: dict, team_code: str) -> list[dict]:
    target_kickoff = _dt(target_fixture.get("kickoff_time"))
    if target_kickoff is None:
        raise ValueError("Team State requires a governed target kickoff time.")
    observations = []
    for fixture in query_lab.load_fixtures():
        kickoff = _dt(fixture.get("kickoff_time"))
        if kickoff is None or kickoff >= target_kickoff:
            continue
        observation = _observation_for_fixture(fixture, team_code)
        if observation is not None:
            observations.append(observation)
    observations.sort(key=lambda row: _dt(row["kickoff_time"]) or datetime.min.replace(tzinfo=timezone.utc))
    return observations


def _mean(values: Iterable[float | None]) -> tuple[float | None, int]:
    observed = [float(value) for value in values if value is not None]
    return ((sum(observed) / len(observed)) if observed else None, len(observed))


def _aligned_ratio(matches: list[dict], numerator: str, denominator: str) -> dict:
    numerator_total = denominator_total = 0.0
    observed = 0
    for match in matches:
        values = match["state_metrics"]
        a, b = _number(values.get(numerator)), _number(values.get(denominator))
        if a is None or b is None:
            continue
        numerator_total += a
        denominator_total += b
        observed += 1
    return {
        "value": (numerator_total / denominator_total) if observed and denominator_total > 0 else None,
        "observed_matches": observed,
        "eligible_matches": len(matches),
        "denominator_total": denominator_total if observed else None,
    }


def _share(matches: list[dict], own: str, against: str) -> dict:
    own_total = against_total = 0.0
    observed = 0
    for match in matches:
        values = match["state_metrics"]
        a, b = _number(values.get(own)), _number(values.get(against))
        if a is None or b is None:
            continue
        own_total += a
        against_total += b
        observed += 1
    denominator = own_total + against_total
    return {
        "value": (own_total / denominator) if observed and denominator > 0 else None,
        "observed_matches": observed,
        "eligible_matches": len(matches),
    }


def _window(name: str, matches: list[dict]) -> dict:
    metrics = []
    for spec in STATE_METRICS:
        value, observed = _mean(match["state_metrics"].get(spec.key) for match in matches)
        metrics.append({
            "key": spec.key,
            "label": spec.label,
            "unit": spec.unit,
            "value": value,
            "eligible_matches": len(matches),
            "observed_matches": observed,
            "missing_matches": len(matches) - observed,
            "coverage_status": (
                "COMPLETE" if observed == len(matches) and matches else "PARTIAL" if observed else "UNAVAILABLE"
            ),
            "representation": spec.representation,
        })

    schedule_strength, schedule_observed = _mean(match.get("opponent_pre_match_ppg") for match in matches)
    xg_representations = sorted({
        str(rep)
        for match in matches
        for rep in (
            match.get("representations", {}).get("expected_goals_for"),
            match.get("representations", {}).get("expected_goals_against"),
        )
        if rep
    })
    return {
        "name": name,
        "sample_size": len(matches),
        "points_per_match": (sum(int(match["points"]) for match in matches) / len(matches)) if matches else None,
        "schedule_strength_opponent_pre_match_ppg": schedule_strength,
        "schedule_strength_observed_matches": schedule_observed,
        "metrics": metrics,
        "derived": {
            "shot_share": _share(matches, "shots_for", "shots_against"),
            "xg_share": _share(matches, "xg_for", "xg_against"),
            "xg_per_shot_for": _aligned_ratio(matches, "xg_for", "shots_for"),
            "xg_per_shot_against": _aligned_ratio(matches, "xg_against", "shots_against"),
        },
        "expected_goal_representations": xg_representations,
        "representation_mixing_detected": len(xg_representations) > 1,
        "contributing_fixtures": [
            {
                "season": match["season"],
                "fixture_id": match["fixture_id"],
                "kickoff_time": match["kickoff_time"],
                "opponent": match["opponent_name"],
                "venue": match["venue"],
                "result": match["result"],
            }
            for match in matches
        ],
    }


def _comparison(recent: dict, baseline: dict) -> dict:
    recent_map = {row["key"]: row.get("value") for row in recent.get("metrics", [])}
    baseline_map = {row["key"]: row.get("value") for row in baseline.get("metrics", [])}
    return {
        "recent_window": recent.get("name"),
        "baseline_window": baseline.get("name"),
        "metric_deltas": {
            key: None if recent_map[key] is None or baseline_map[key] is None else float(recent_map[key]) - float(baseline_map[key])
            for key in sorted(set(recent_map) & set(baseline_map))
        },
        "points_per_match_delta": (
            None
            if recent.get("points_per_match") is None or baseline.get("points_per_match") is None
            else float(recent["points_per_match"]) - float(baseline["points_per_match"])
        ),
    }


def _target_fixture(season: str, fixture_id: str) -> dict:
    target = next(
        (
            dict(row)
            for row in query_lab.load_fixtures()
            if str(row.get("season") or "") == str(season)
            and str(row.get("fixture_id") or "") == str(fixture_id)
        ),
        None,
    )
    if target is None:
        raise ValueError(f"Target fixture not found: {season}/{fixture_id}.")
    return target


def build_team_state(
    season: str,
    fixture_id: str,
    team_code: str,
    *,
    recent_windows: tuple[int, ...] = DEFAULT_RECENT_WINDOWS,
) -> dict:
    target = _target_fixture(season, fixture_id)
    target_context = _fixture_side_for_team(target, str(team_code))
    if target_context is None:
        raise ValueError(f"Team {team_code} is not part of target fixture {season}/{fixture_id}.")
    side, opponent = target_context

    observations = _preceding_observations(target, str(team_code))
    current_season = [row for row in observations if row["season"] == str(season)]
    previous_season = _previous_season(str(season))
    prior_season_rows = [row for row in observations if previous_season and row["season"] == previous_season]

    windows: dict[str, dict] = {}
    for limit in recent_windows:
        selected = observations[-int(limit):] if limit > 0 else []
        windows[f"recent_{limit}"] = _window(f"recent_{limit}", selected)
    windows["season_to_date"] = _window("season_to_date", current_season)
    windows["prior_season"] = _window("prior_season", prior_season_rows)

    recent_key = f"recent_{recent_windows[0]}" if recent_windows else "season_to_date"
    return {
        "state_version": STATE_VERSION,
        "season": str(season),
        "fixture_id": str(fixture_id),
        "as_of": target.get("kickoff_time"),
        "team": {
            "persistent_team_code": str(team_code),
            "side": side,
            "opponent_team_code": opponent.get("persistent_team_code"),
            "opponent_name": opponent.get("display_name"),
        },
        "windows": windows,
        "change_vs_prior_season": _comparison(windows[recent_key], windows["prior_season"]),
        "temporal_contract": {
            "target_kickoff_enforced": True,
            "future_fixture_exclusion": "kickoff_time >= target kickoff is excluded",
            "contributing_fixture_rule": "completed canonical Premier League fixtures strictly before target kickoff",
            "information_availability_status": "OPERATIONAL_ASSUMPTION_NOT_SOURCE_TIMESTAMP_PROVEN",
            "information_availability_note": (
                "V1 uses final statistics from completed prior fixtures. Event-time ordering is enforced, "
                "but the preserved source does not yet prove the exact historical publication timestamp of every statistic."
            ),
            "predictive_research_status": "EXPERIMENTAL_UNTIL_INFORMATION_AVAILABILITY_AUDIT",
        },
        "limitations": [
            "V1 is an interpretable team-state slice, not a claim that these metrics are predictive.",
            "Opponent strength uses opponent pre-match Premier League points per game as transparent schedule context; it is not yet a latent-strength adjustment.",
            "Expected-goals state uses only the governed player-match-derived representation and remains unavailable before that representation exists.",
            "Short windows may cross a season boundary; every contributing fixture and representation is retained for inspection.",
        ],
    }


def fixture_team_states(season: str, fixture_id: str) -> dict:
    target = _target_fixture(season, fixture_id)
    home_code = _team_code_for_side(target, "home")
    away_code = _team_code_for_side(target, "away")
    return {
        "state_version": STATE_VERSION,
        "season": str(season),
        "fixture_id": str(fixture_id),
        "as_of": target.get("kickoff_time"),
        "home": build_team_state(season, fixture_id, home_code),
        "away": build_team_state(season, fixture_id, away_code),
    }


__all__ = [
    "DEFAULT_RECENT_WINDOWS",
    "STATE_METRICS",
    "STATE_VERSION",
    "build_team_state",
    "fixture_team_states",
]
