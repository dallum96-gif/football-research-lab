from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import query_api
import source_family_adapters
import variable_resolver


app = FastAPI(title="Football Research Laboratory API", version="0.2.0")


class PlayerLeader(BaseModel):
    player_id: str | None = None
    player_name: str | None = None
    position: str | None = None
    minutes: float | None = None
    value: float | None = None
    secondary_value: float | None = None


class PlayerMetric(BaseModel):
    key: str
    label: str
    unit: str
    secondary_label: str | None = None
    secondary_unit: str | None = None
    player: PlayerLeader | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    status: str = "AVAILABLE"


class PlayerPerformanceSide(BaseModel):
    side: str
    team_name: str
    metrics: list[PlayerMetric]
    status: str
    limitations: list[str] = Field(default_factory=list)


class FixturePlayerPerformanceResponse(BaseModel):
    season: str
    fixture_id: str
    home: PlayerPerformanceSide
    away: PlayerPerformanceSide


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _percentage(numerator: object, denominator: object) -> float | None:
    numerator_value = _number(numerator)
    denominator_value = _number(denominator)
    if numerator_value is None or denominator_value in (None, 0):
        return None
    return numerator_value / denominator_value * 100.0


def _identity_details(season: str, source_player_id: str | None) -> tuple[str | None, str | None]:
    if not source_player_id:
        return None, None
    try:
        resolved = source_family_adapters.source_player_season_identity(season, source_player_id)
    except (FileNotFoundError, ValueError):
        return None, None
    player_season = resolved.get("player_season") or {}
    name = player_season.get("playerName") or player_season.get("displayName")
    position = player_season.get("position")
    return (
        str(name).strip() if name not in (None, "") else None,
        str(position).strip() if position not in (None, "") else None,
    )


def _resolved_values(name: str, season: str, fixture_id: str) -> dict[str, dict]:
    try:
        result = variable_resolver.resolve_variable(
            name,
            season=season,
            fixture_id=fixture_id,
            family="player_match",
        )
    except (variable_resolver.VariableResolutionError, ValueError) as exc:
        return {"__error__": {"error": str(exc)}}
    return {
        str(item.get("source_player_id")): item
        for item in result.get("results", [])
        if item.get("source_player_id") not in (None, "")
    }


def _player_minutes(season: str, fixture_id: str) -> dict[str, float | None]:
    resolved = _resolved_values("minutesPlayed", season, fixture_id)
    return {
        player_id: _number(item.get("value"))
        for player_id, item in resolved.items()
        if player_id != "__error__"
    }


def _leader(
    season: str,
    values: dict[str, dict],
    *,
    team_source_id: str,
    minutes_by_player: dict[str, float | None],
) -> PlayerLeader | None:
    candidates: list[tuple[float, str, str, dict]] = []
    for source_player_id, item in values.items():
        if source_player_id == "__error__":
            continue
        if str(item.get("source_team_id", "")).strip() != team_source_id:
            continue
        value = _number(item.get("value"))
        if value is None:
            continue
        minutes = minutes_by_player.get(source_player_id)
        if minutes is not None and minutes <= 0:
            continue
        name, position = _identity_details(season, source_player_id)
        display_name = name or source_player_id
        candidates.append((value, display_name.casefold(), source_player_id, {
            "id": source_player_id,
            "value": value,
            "minutes": minutes,
            "position": position,
            "name": name,
        }))

    if not candidates:
        return None

    _, _, _, selected = max(candidates, key=lambda item: (item[0], item[1], item[2]))
    return PlayerLeader(
        player_id=selected["id"],
        player_name=selected["name"],
        position=selected["position"],
        minutes=selected["minutes"],
        value=selected["value"],
    )


def _side(
    season: str,
    side: str,
    team_name: str,
    team_source_id: str,
    minutes_by_player: dict[str, float | None],
    resolved: dict[str, dict[str, dict]],
) -> PlayerPerformanceSide:
    passes = _leader(season, resolved["accuratePass"], team_source_id=team_source_id, minutes_by_player=minutes_by_player)
    tackles = _leader(season, resolved["wonTackle"], team_source_id=team_source_id, minutes_by_player=minutes_by_player)
    interceptions = _leader(season, resolved["interceptionWon"], team_source_id=team_source_id, minutes_by_player=minutes_by_player)
    key_passes = _leader(season, resolved["keyPass"], team_source_id=team_source_id, minutes_by_player=minutes_by_player)
    dribbles = _leader(season, resolved["successfulDribbles"], team_source_id=team_source_id, minutes_by_player=minutes_by_player)
    shots = _leader(season, resolved["onTargetScoringAttempt"], team_source_id=team_source_id, minutes_by_player=minutes_by_player)

    total_passes = resolved["totalPass"].get(passes.player_id) if passes and passes.player_id else None
    total_tackles = resolved["totalTackle"].get(tackles.player_id) if tackles and tackles.player_id else None
    unsuccessful_dribbles = resolved["unsuccessfulDribbles"].get(dribbles.player_id) if dribbles and dribbles.player_id else None

    if passes and total_passes:
        passes.secondary_value = _percentage(passes.value, total_passes.get("value"))
    if tackles and total_tackles:
        tackles.secondary_value = _percentage(tackles.value, total_tackles.get("value"))
    if dribbles and unsuccessful_dribbles:
        unsuccessful_value = _number(unsuccessful_dribbles.get("value"))
        if unsuccessful_value is not None and dribbles.value is not None:
            dribbles.secondary_value = _percentage(dribbles.value, dribbles.value + unsuccessful_value)

    definitions = (
        ("passes_completed", "Passes completed", "Pass completion", passes),
        ("tackles_won", "Tackles won", "Tackle won", tackles),
        ("interceptions_won", "Interceptions", None, interceptions),
        ("key_passes", "Key passes", None, key_passes),
        ("successful_dribbles", "Successful dribbles", "Dribble success", dribbles),
        ("shots_on_target", "Shots on target", None, shots),
    )

    metrics: list[PlayerMetric] = []
    for key, label, secondary_label, player in definitions:
        metrics.append(
            PlayerMetric(
                key=key,
                label=label,
                unit="",
                secondary_label=secondary_label,
                secondary_unit="%" if secondary_label else None,
                player=player,
                status="AVAILABLE" if player else "UNAVAILABLE",
                provenance={
                    "resolver": "variable_resolver.resolve_variable",
                    "family": "player_match",
                },
            )
        )

    return PlayerPerformanceSide(
        side=side,
        team_name=team_name,
        metrics=metrics,
        status="AVAILABLE" if any(metric.player for metric in metrics) else "UNAVAILABLE",
        limitations=[
            "Values are retrieved through the Universal Variable Resolver; missing source observations remain unavailable.",
        ],
    )


@app.get(
    "/api/v1/fixtures/{season}/{fixture_id}/player-performance",
    response_model=FixturePlayerPerformanceResponse,
)
def fixture_player_performance(season: str, fixture_id: str) -> FixturePlayerPerformanceResponse:
    try:
        fixture = query_api.fixture_detail(season, fixture_id)["fixture"]
        resolved_match = source_family_adapters.resolve_source_match(season, fixture_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fixture player-performance access failed safely.") from exc

    resolved: dict[str, dict[str, dict]] = {}
    for variable_name in (
        "minutesPlayed",
        "totalPass",
        "accuratePass",
        "totalTackle",
        "wonTackle",
        "interceptionWon",
        "keyPass",
        "successfulDribbles",
        "unsuccessfulDribbles",
        "onTargetScoringAttempt",
    ):
        resolved[variable_name] = _resolved_values(variable_name, season, fixture_id)

    minutes_by_player = {
        player_id: _number(item.get("value"))
        for player_id, item in resolved["minutesPlayed"].items()
        if player_id != "__error__"
    }

    home_source_id = str(resolved_match["home"].get("team_id", "")).strip()
    away_source_id = str(resolved_match["away"].get("team_id", "")).strip()

    return FixturePlayerPerformanceResponse(
        season=season,
        fixture_id=str(fixture_id),
        home=_side(
            season,
            "home",
            str(fixture["home_team_name"]),
            home_source_id,
            minutes_by_player,
            resolved,
        ),
        away=_side(
            season,
            "away",
            str(fixture["away_team_name"]),
            away_source_id,
            minutes_by_player,
            resolved,
        ),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "football-research-laboratory-api"}
