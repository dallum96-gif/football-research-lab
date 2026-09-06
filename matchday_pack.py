from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import poisson_model
import query_api
import query_lab
import team_research_stats


ROOT = Path(__file__).resolve().parent
FPL_PLAYER_GW = ROOT / "data" / "fpl_player_gw_evidence.csv"
MODEL_VERSION = "matchday-stat-pack-v1"
RECENT_MATCH_LIMIT = 5

TEAM_METRICS = (
    ("goals_for", "Goals", "goals"),
    ("goals_against", "Goals conceded", "goals"),
    ("Shots", "Shots", "shots"),
    ("Shots on target", "Shots on target", "shots"),
    ("Expected goals", "xG", "xG"),
    ("Big chances created", "Big chances", "chances"),
    ("Corners", "Corners", "corners"),
    ("Yellow cards", "Yellow cards", "cards"),
)

PLAYER_METRICS = (
    ("goals", "Goals", "source_goals_scored", "goals"),
    ("xg", "xG", "source_expected_goals", "xG"),
    ("assists", "Assists", "source_assists", "assists"),
    ("xa", "xA", "source_expected_assists", "xA"),
    ("cards", "Cards", "__cards__", "cards"),
    ("tackles", "Tackles", "source_tackles", "tackles"),
    ("recoveries", "Recoveries", "source_recoveries", "recoveries"),
    (
        "defensive_contribution",
        "Defensive contribution",
        "source_defensive_contribution",
        "actions",
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
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def _identity_index() -> dict[tuple[str, str], dict]:
    index: dict[tuple[str, str], dict] = {}
    for row in query_lab.load_identity_registry():
        if str(row.get("mapping_status") or "") != "VERIFIED":
            continue
        season = str(row.get("season") or "").strip()
        local_id = str(row.get("local_team_id") or "").strip()
        if not season or not local_id:
            continue
        index[(season, local_id)] = {
            "persistent_team_code": str(row.get("persistent_team_code") or "").strip(),
            "display_name": str(row.get("canonical_name") or "").replace("_", " ").strip(),
        }
    return index


def _identity(season: str, local_id: object) -> dict:
    result = _identity_index().get((str(season), str(local_id)))
    if result is None:
        raise ValueError(f"No verified team identity for {season}/{local_id}.")
    return result


@lru_cache(maxsize=1)
def _fpl_rows() -> tuple[dict, ...]:
    if not FPL_PLAYER_GW.exists():
        return tuple()
    with FPL_PLAYER_GW.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def _fixture_before(row: dict, target_kickoff: datetime) -> bool:
    kickoff = _dt(row.get("kickoff_time"))
    return kickoff is not None and kickoff < target_kickoff


def _completed(row: dict) -> bool:
    return row.get("home_score") not in (None, "") and row.get("away_score") not in (None, "")


def _team_metric_row(season: str, team_code: str, fixture_id: object) -> dict:
    return next(
        (
            row
            for row in team_research_stats.team_match_stats(season, team_code)
            if str(row.get("fixture_id")) == str(fixture_id)
        ),
        {},
    )


def _result(goals_for: float, goals_against: float) -> str:
    if goals_for > goals_against:
        return "W"
    if goals_for < goals_against:
        return "L"
    return "D"


def _recent_team_side(fixture: dict, side: str) -> dict:
    season = str(fixture["season"])
    local_id = str(fixture[f"{side}_team_id"])
    team_identity = _identity(season, local_id)
    team_code = team_identity["persistent_team_code"]
    target_kickoff = _dt(fixture.get("kickoff_time"))
    if target_kickoff is None:
        raise ValueError("Matchday research requires a governed fixture kickoff time.")

    candidates: list[dict] = []
    for row in query_lab.load_fixtures():
        if not _completed(row) or not _fixture_before(row, target_kickoff):
            continue
        row_season = str(row.get("season") or "")
        home_identity = _identity_index().get((row_season, str(row.get("home_team_id") or "")))
        away_identity = _identity_index().get((row_season, str(row.get("away_team_id") or "")))
        if home_identity is None or away_identity is None:
            continue

        if home_identity["persistent_team_code"] == team_code:
            is_home = True
            opponent = away_identity["display_name"]
            goals_for = float(row["home_score"])
            goals_against = float(row["away_score"])
        elif away_identity["persistent_team_code"] == team_code:
            is_home = False
            opponent = home_identity["display_name"]
            goals_for = float(row["away_score"])
            goals_against = float(row["home_score"])
        else:
            continue

        metric_row = _team_metric_row(row_season, team_code, row.get("fixture_id"))
        candidates.append(
            {
                "season": row_season,
                "fixture_id": str(row.get("fixture_id") or ""),
                "kickoff_time": row.get("kickoff_time"),
                "opponent": opponent,
                "venue": "Home" if is_home else "Away",
                "goals_for": goals_for,
                "goals_against": goals_against,
                "result": _result(goals_for, goals_against),
                "metrics": metric_row,
            }
        )

    candidates.sort(
        key=lambda row: (_dt(row.get("kickoff_time")) or datetime.min.replace(tzinfo=timezone.utc)),
        reverse=True,
    )
    matches = candidates[:RECENT_MATCH_LIMIT]

    metrics = []
    for key, label, unit in TEAM_METRICS:
        values: list[float] = []
        for match in matches:
            if key in {"goals_for", "goals_against"}:
                value = _number(match.get(key))
            else:
                value = _number(match.get("metrics", {}).get(key))
            if value is not None:
                values.append(value)
        metrics.append(
            {
                "key": key,
                "label": label,
                "unit": unit,
                "value": (sum(values) / len(values)) if values else None,
                "observed_matches": len(values),
                "eligible_matches": len(matches),
            }
        )

    points = sum(3 if row["result"] == "W" else 1 if row["result"] == "D" else 0 for row in matches)
    return {
        "team_name": team_identity["display_name"],
        "persistent_team_code": team_code,
        "sample_size": len(matches),
        "current_season_sample_size": sum(1 for row in matches if row["season"] == season),
        "form": [row["result"] for row in reversed(matches)],
        "points": points,
        "matches": matches,
        "metrics": metrics,
        "as_of": fixture.get("kickoff_time"),
    }


def _player_display_name(row: dict) -> str:
    parts = [
        str(row.get("source_first_name") or "").strip(),
        str(row.get("source_second_name") or "").strip(),
    ]
    return " ".join(part for part in parts if part) or str(row.get("source_player_code") or "Player")


def _observed_player_metric(recent: list[dict], source_key: str) -> tuple[float | None, int]:
    values: list[float] = []
    if source_key == "__cards__":
        for row in recent:
            yellow = _number(row.get("source_yellow_cards"))
            red = _number(row.get("source_red_cards"))
            if yellow is None or red is None:
                continue
            values.append(yellow + red)
    else:
        for row in recent:
            value = _number(row.get(source_key))
            if value is not None:
                values.append(value)
    return (sum(values) if values else None, len(values))


def _player_recent_side(fixture: dict, side: str) -> dict:
    season = str(fixture["season"])
    local_id = str(fixture[f"{side}_team_id"])
    team_identity = _identity(season, local_id)
    team_name = team_identity["display_name"]
    persistent_team_code = team_identity["persistent_team_code"]
    target_kickoff = _dt(fixture.get("kickoff_time"))
    if target_kickoff is None:
        raise ValueError("Matchday research requires a governed fixture kickoff time.")

    fixture_times = {
        str(row.get("fixture_id")): _dt(row.get("kickoff_time"))
        for row in query_lab.load_fixtures()
        if str(row.get("season")) == season
    }

    by_player: dict[str, list[dict]] = defaultdict(list)
    observed_fixture_ids: set[str] = set()
    for row in _fpl_rows():
        if str(row.get("frl_season") or "") != season:
            continue
        # FPL evidence is keyed to the persistent FRL club code, not the season-local fixture id.
        if str(row.get("frl_team_id") or "") != persistent_team_code:
            continue
        if str(row.get("frl_fixture_relationship_status") or "") != "VERIFIED":
            continue
        minutes = _number(row.get("source_minutes")) or 0.0
        if minutes <= 0:
            continue
        fixture_id = str(row.get("frl_fixture_id") or "")
        kickoff = fixture_times.get(fixture_id)
        if kickoff is None or kickoff >= target_kickoff:
            continue
        identity_key = str(row.get("frl_player_identity_key") or row.get("source_player_code") or "").strip()
        if not identity_key:
            continue
        observed_fixture_ids.add(fixture_id)
        copy = dict(row)
        copy["_kickoff"] = kickoff
        by_player[identity_key].append(copy)

    players = []
    for identity_key, rows in by_player.items():
        rows.sort(key=lambda row: row["_kickoff"], reverse=True)
        recent = rows[:RECENT_MATCH_LIMIT]
        first = recent[0]
        totals: dict[str, float | None] = {}
        observed: dict[str, int] = {}
        for key, _label, source_key, _unit in PLAYER_METRICS:
            total, observed_matches = _observed_player_metric(recent, source_key)
            totals[key] = total
            observed[key] = observed_matches

        players.append(
            {
                "player_identity_key": identity_key,
                "player_code": str(first.get("source_player_code") or ""),
                "player_name": _player_display_name(first),
                "position": str(first.get("source_position") or ""),
                "appearances": len(recent),
                "minutes": sum(_number(row.get("source_minutes")) or 0.0 for row in recent),
                "totals": totals,
                "observed": observed,
            }
        )

    leaderboards = []
    for key, label, _source_key, unit in PLAYER_METRICS:
        eligible = [player for player in players if player["totals"].get(key) is not None]
        ranked = sorted(
            eligible,
            key=lambda player: (-float(player["totals"][key]), player["player_name"].casefold()),
        )[:5]
        leaderboards.append(
            {
                "key": key,
                "label": label,
                "unit": unit,
                "players": [
                    {
                        "rank": index,
                        "player_code": player["player_code"],
                        "player_name": player["player_name"],
                        "position": player["position"],
                        "appearances": player["appearances"],
                        "observed_appearances": player["observed"].get(key, 0),
                        "minutes": player["minutes"],
                        "value": float(player["totals"][key]),
                    }
                    for index, player in enumerate(ranked, start=1)
                ],
            }
        )

    return {
        "team_name": team_name,
        "sample_definition": "up to five most recent player appearances before kickoff in the selected season",
        "player_count": len(players),
        "fixture_evidence_count": len(observed_fixture_ids),
        "leaderboards": leaderboards,
        "source": "governed FPL player-gameweek evidence",
    }


def _previous_season(season: str) -> str | None:
    seasons = sorted(str(value) for value in query_api.list_seasons())
    try:
        index = seasons.index(season)
    except ValueError:
        return None
    return seasons[index - 1] if index > 0 else None


def _prediction(fixture: dict) -> dict:
    home = str(fixture["home_team_name"])
    away = str(fixture["away_team_name"])
    season = str(fixture["season"])
    try:
        if season == poisson_model.TARGET_SEASON:
            prediction = poisson_model.poisson_prediction(home, away)
        else:
            source_season = _previous_season(season)
            if source_season is None:
                raise ValueError("No prior represented Premier League season is available.")
            prediction = poisson_model.prediction_for_source_season(
                home,
                away,
                source_season,
                target_season=season,
            )
        representations = {
            str((prediction.get("inputs") or {}).get("home_representation") or ""),
            str((prediction.get("inputs") or {}).get("away_representation") or ""),
        }
        research_status = (
            "EXPERIMENTAL_PROMOTED_PRIOR"
            if "PROMOTED_BLEND" in representations
            else "BASELINE_VALIDATED_CONTINUING_TEAMS"
        )
        return {**prediction, "status": "AVAILABLE", "research_status": research_status}
    except ValueError as exc:
        return {
            "status": "UNAVAILABLE",
            "model": poisson_model.MODEL_VERSION,
            "research_status": "UNAVAILABLE",
            "reason": str(exc),
        }


def fixture_options(season: str) -> list[dict]:
    rows = query_api.fixtures(season=season, team=None, limit=500)["results"]
    return [
        {
            "season": season,
            "fixture_id": str(row["fixture_id"]),
            "gameweek": int(row["gameweek"]) if row.get("gameweek") not in (None, "") else None,
            "kickoff_time": row.get("kickoff_time"),
            "home_team_name": row["home_team_name"],
            "away_team_name": row["away_team_name"],
            "completed": _completed(row),
        }
        for row in rows
    ]


def build_matchday_pack(season: str, fixture_id: str) -> dict:
    detail = query_api.fixture_detail(season=season, fixture_id=fixture_id)
    fixture = dict(detail["fixture"])
    prediction = _prediction(fixture)
    teams = {
        "home": _recent_team_side(fixture, "home"),
        "away": _recent_team_side(fixture, "away"),
    }
    players = {
        "home": _player_recent_side(fixture, "home"),
        "away": _player_recent_side(fixture, "away"),
    }

    current_team_min = min(
        int(teams["home"]["current_season_sample_size"]),
        int(teams["away"]["current_season_sample_size"]),
    )
    current_player_min = min(
        int(players["home"]["fixture_evidence_count"]),
        int(players["away"]["fixture_evidence_count"]),
    )
    early_season = current_team_min < RECENT_MATCH_LIMIT or current_player_min < RECENT_MATCH_LIMIT

    return {
        "pack_version": MODEL_VERSION,
        "fixture": fixture,
        "as_of": fixture.get("kickoff_time"),
        "prediction": prediction,
        "data_maturity": {
            "status": "EARLY_SEASON" if early_season else "RECENT_WINDOW_MATURE",
            "team_current_season_matches": {
                "home": teams["home"]["current_season_sample_size"],
                "away": teams["away"]["current_season_sample_size"],
            },
            "player_fixture_evidence_matches": {
                "home": players["home"]["fixture_evidence_count"],
                "away": players["away"]["fixture_evidence_count"],
            },
            "prediction_research_status": prediction.get("research_status"),
            "note": (
                "Early-season current campaign evidence is still thin. Team Last 5 can bridge the summer through governed persistent club identity; Player Last 5 remains current-season only."
                if early_season
                else "Both teams have a full five-match current-season recent window and at least five current-season player-evidence fixtures before kickoff."
            ),
        },
        "teams": teams,
        "players": players,
        "matchups": {
            "cards": {
                "status": "PARTIAL",
                "available_now": [
                    "player card totals from governed FPL player-gameweek evidence",
                    "player tackles and defensive contribution where observed",
                ],
                "withheld": [
                    "fouls committed versus fouls drawn opponent pairing",
                    "referee-adjusted card matchup probability",
                ],
                "note": (
                    "FRL can surface card and defensive-action context now, but does not yet "
                    "claim a governed foul-based player-v-player card model."
                ),
            }
        },
        "market": {
            "status": "MANUAL_INPUT",
            "note": (
                "Bookmaker decimal odds are entered locally in the Matchday workspace and "
                "compared with FRL fair odds; no bookmaker feed is required for V1."
            ),
        },
        "limitations": [
            "Team Last 5 is reconstructed strictly from completed canonical fixtures before the selected kickoff.",
            "Rich team-match fields can be partially observed when the five-match window crosses a source-coverage boundary.",
            "Player Last 5 currently uses governed FPL player-gameweek evidence from the selected season only.",
            "H2H and foul-based card matchup modelling are not yet promoted into V1 predictive evidence.",
        ],
    }


__all__ = ["MODEL_VERSION", "build_matchday_pack", "fixture_options"]
