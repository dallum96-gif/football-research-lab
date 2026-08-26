from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import query_api
import source_family_adapters
import variable_resolver

router = APIRouter()


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


def _fixture_player_identity(fixture: dict) -> dict[str, dict[str, Any]]:
    """Build display identity from the same fixture's Player–Fixture evidence."""
    identity: dict[str, dict[str, Any]] = {}
    for row in source_family_adapters.player_match_source_rows(
        str(fixture["season"]), str(fixture["fixture_id"])
    ):
        player_id = str(row.get("playerId") or row.get("pl_code") or "").strip()
        if not player_id:
            continue

        name = row.get("playerName") or row.get("displayName")
        position = row.get("position")
        minutes = _number(row.get("minutesPlayed"))
        team_source_id = str(row.get("team_id") or "").strip()

        identity.setdefault(
            player_id,
            {
                "name": str(name).strip() if name not in (None, "") else None,
                "position": str(position).strip() if position not in (None, "") else None,
                "minutes": minutes,
                "team_source_id": team_source_id,
            },
        )

    return identity


def _resolved_values(name: str, season: str, fixture_id: str, *, family: str = "player_match") -> dict:
    try:
        result = variable_resolver.resolve_variable(
            name,
            season=season,
            fixture_id=fixture_id,
            family=family,
        )
    except (variable_resolver.VariableResolutionError, ValueError) as exc:
        return {"__error__": {"error": str(exc)}}

    if family == "fpl":
        return {
            str(item.get("player_id")): item
            for item in result.get("results", [])
            if item.get("player_id") not in (None, "")
        }

    return {
        str(item.get("source_player_id")): item
        for item in result.get("results", [])
        if item.get("source_player_id") not in (None, "")
    }


def _leader(
    values: dict[str, dict],
    *,
    team_source_id: str,
    identity_by_player: dict[str, dict[str, Any]],
) -> PlayerLeader | None:
    candidates: list[tuple[float, str, str, dict]] = []

    for source_player_id, item in values.items():
        if source_player_id == "__error__":
            continue
        item_team_id = str(item.get("source_team_id", "")).strip()
        if item_team_id and item_team_id != team_source_id:
            continue

        value = _number(item.get("value"))
        if value is None:
            continue

        identity = identity_by_player.get(source_player_id)
        if not identity or not identity.get("name"):
            continue
        if identity.get("team_source_id") not in ("", team_source_id):
            continue

        selected = {
            "id": source_player_id,
            "value": value,
            "minutes": identity.get("minutes"),
            "position": identity.get("position"),
            "name": identity.get("name"),
        }
        candidates.append((value, str(selected["name"]).casefold(), source_player_id, selected))

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


def _fpl_dribbles_leader(values: dict[str, dict], *, home: bool) -> PlayerLeader | None:
    candidates: list[tuple[float, str, str, dict]] = []
    for player_id, item in values.items():
        raw_home = str(item.get("was_home", "")).strip().lower()
        row_home = raw_home in {"true", "1", "yes"}
        if row_home != home:
            continue

        value = _number(item.get("value"))
        name = str(item.get("player_name") or "").strip()
        if value is None or not name:
            continue

        selected = {
            "id": f"fpl:{player_id}",
            "name": name,
            "minutes": _number(item.get("minutes")),
            "value": value,
        }
        candidates.append((value, name.casefold(), str(player_id), selected))

    if not candidates:
        return None

    _, _, _, selected = max(candidates, key=lambda item: (item[0], item[1], item[2]))
    return PlayerLeader(
        player_id=selected["id"],
        player_name=selected["name"],
        minutes=selected["minutes"],
        value=selected["value"],
    )


def _side(
    side: str,
    team_name: str,
    team_source_id: str,
    identity_by_player: dict[str, dict[str, Any]],
    resolved: dict[str, dict[str, dict]],
) -> PlayerPerformanceSide:
    passes = _leader(resolved["totalPass"], team_source_id=team_source_id, identity_by_player=identity_by_player)
    tackles = _leader(resolved["totalTackle"], team_source_id=team_source_id, identity_by_player=identity_by_player)
    interceptions = _leader(resolved["interceptionWon"], team_source_id=team_source_id, identity_by_player=identity_by_player)
    key_passes = _leader(resolved["keyPass"], team_source_id=team_source_id, identity_by_player=identity_by_player)
    shots = _leader(resolved["onTargetScoringAttempt"], team_source_id=team_source_id, identity_by_player=identity_by_player)
    dribbles = _fpl_dribbles_leader(resolved["dribbles"], home=side == "home")

    if passes and passes.player_id:
        accurate_passes = resolved["accuratePass"].get(passes.player_id)
        if accurate_passes:
            passes.secondary_value = _percentage(accurate_passes.get("value"), passes.value)
    if tackles and tackles.player_id:
        won_tackle = resolved["wonTackle"].get(tackles.player_id)
        if won_tackle:
            tackles.secondary_value = _percentage(won_tackle.get("value"), tackles.value)

    definitions = (
        ("passes_completed", "Passes", "Pass completion", passes),
        ("tackles_won", "Tackles", "Tackle won", tackles),
        ("interceptions_won", "Interceptions", None, interceptions),
        ("key_passes", "Key passes", None, key_passes),
        ("dribbles", "Dribbles", None, dribbles),
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
                    "family": "fpl" if key == "dribbles" else "player_match",
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
            "Player display identity is taken from the fixture's verified Player–Fixture evidence for PL player-match metrics.",
            "Dribbles are retrieved from the historical FPL player-fixture evidence through the FPL Universal Variable Access seam.",
        ],
    )


@router.get(
    "/api/v1/fixtures/{season}/{fixture_id}/player-performance",
    response_model=FixturePlayerPerformanceResponse,
)
def fixture_player_performance(season: str, fixture_id: str) -> FixturePlayerPerformanceResponse:
    try:
        fixture = query_api.fixture_detail(season, fixture_id)["fixture"]
        resolved_match = source_family_adapters.resolve_source_match(season, fixture_id)
        identity_by_player = _fixture_player_identity(fixture)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fixture player-performance access failed safely.") from exc

    resolved: dict[str, dict[str, dict]] = {}
    for variable_name in (
        "totalPass",
        "accuratePass",
        "totalTackle",
        "wonTackle",
        "interceptionWon",
        "keyPass",
        "onTargetScoringAttempt",
    ):
        resolved[variable_name] = _resolved_values(variable_name, season, fixture_id)
    resolved["dribbles"] = _resolved_values("dribbles", season, fixture_id, family="fpl")

    home_source_id = str(resolved_match["home"].get("team_id", "")).strip()
    away_source_id = str(resolved_match["away"].get("team_id", "")).strip()

    return FixturePlayerPerformanceResponse(
        season=season,
        fixture_id=str(fixture_id),
        home=_side("home", str(fixture["home_team_name"]), home_source_id, identity_by_player, resolved),
        away=_side("away", str(fixture["away_team_name"]), away_source_id, identity_by_player, resolved),
    )
