from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import player_match_stats
import query_api


class PlayerPerformance(BaseModel):
    player_id: str | None = None
    player_name: str | None = None
    position: str | None = None
    minutes: float | None = None
    value: float | None = None
    secondary_value: float | None = None


class PerformanceMetric(BaseModel):
    key: str
    label: str
    unit: str
    secondary_label: str | None = None
    secondary_unit: str | None = None
    player: PlayerPerformance | None = None


class FixturePlayerPerformance(BaseModel):
    side: Literal["home", "away"]
    team_name: str
    metrics: list[PerformanceMetric]
    status: Literal["AVAILABLE", "UNAVAILABLE", "KNOWN_EXCEPTION"]
    limitations: list[str] = Field(default_factory=list)


class FixturePlayerPerformanceResponse(BaseModel):
    season: str
    fixture_id: str
    home: FixturePlayerPerformance
    away: FixturePlayerPerformance


METRICS = (
    ("passes_completed", "Passes completed", "", "Pass completion", "%"),
    ("tackles_won", "Tackles won", "", "Tackle won", "%"),
    ("interceptions_won", "Interceptions won", "", None, None),
    ("key_passes", "Key passes", "", None, None),
    ("successful_dribbles", "Successful dribbles", "", "Dribble success", "%"),
    ("shots_on_target", "Shots on target", "", "Shot accuracy", "%"),
)


def _number(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _percentage(numerator, denominator):
    numerator_value = _number(numerator)
    denominator_value = _number(denominator)
    if numerator_value is None or denominator_value in (None, 0):
        return None
    return numerator_value / denominator_value * 100.0


def _metric_values(row: dict, key: str) -> tuple[float | None, float | None]:
    if key == "passes_completed":
        return _number(row.get("accuratePass")), _percentage(row.get("accuratePass"), row.get("totalPass"))
    if key == "tackles_won":
        return _number(row.get("wonTackle")), _percentage(row.get("wonTackle"), row.get("totalTackle"))
    if key == "interceptions_won":
        return _number(row.get("interceptionWon")), None
    if key == "key_passes":
        return _number(row.get("keyPass")), None
    if key == "successful_dribbles":
        successful = _number(row.get("successfulDribbles"))
        unsuccessful = _number(row.get("unsuccessfulDribbles"))
        total = None if successful is None and unsuccessful is None else (successful or 0.0) + (unsuccessful or 0.0)
        return successful, _percentage(successful, total)
    if key == "shots_on_target":
        on_target = _number(row.get("onTargetScoringAttempt"))
        total_shots = _number(row.get("totalScoringAttempt"))
        return on_target, _percentage(on_target, total_shots)
    raise KeyError(key)


def _name(row: dict) -> str | None:
    explicit = row.get("playerName") or row.get("name") or row.get("player")
    if explicit:
        value = str(explicit).strip().replace("_", " ")
        if value:
            return value
    first = str(row.get("first_name") or "").strip()
    second = str(row.get("second_name") or "").strip()
    value = " ".join(part for part in (first, second) if part)
    return value or None


def _eligible_rows(rows: tuple[dict, ...], side: str) -> tuple[dict, ...]:
    eligible = []
    for row in rows:
        venue = str(row.get("venue") or "").strip().lower()
        if venue != side:
            continue
        minutes = _number(row.get("minutesPlayed"))
        if minutes is not None and minutes > 0:
            eligible.append(row)
    return tuple(eligible)


def _leader(rows: tuple[dict, ...], key: str) -> PlayerPerformance | None:
    candidates = []
    for row in rows:
        value, secondary_value = _metric_values(row, key)
        if value is None:
            continue
        candidates.append((value, _name(row) or "", str(player_match_stats.source_player_id(row) or ""), row, secondary_value))

    if not candidates:
        return None

    value, _, _, row, secondary_value = max(candidates, key=lambda item: (item[0], item[1].casefold(), item[2]))
    return PlayerPerformance(
        player_id=player_match_stats.source_player_id(row),
        player_name=_name(row),
        position=str(row.get("position") or row.get("positionText") or "").strip() or None,
        minutes=_number(row.get("minutesPlayed")),
        value=value,
        secondary_value=secondary_value,
    )


def _side_payload(
    rows: tuple[dict, ...],
    side: Literal["home", "away"],
    team_name: str,
    limitation: str | None = None,
) -> FixturePlayerPerformance:
    eligible = _eligible_rows(rows, side)
    metrics = [
        PerformanceMetric(
            key=key,
            label=label,
            unit=unit,
            secondary_label=secondary_label,
            secondary_unit=secondary_unit,
            player=_leader(eligible, key),
        )
        for key, label, unit, secondary_label, secondary_unit in METRICS
    ]
    status: Literal["AVAILABLE", "UNAVAILABLE", "KNOWN_EXCEPTION"] = "AVAILABLE" if eligible else "UNAVAILABLE"
    limitations: list[str] = []
    if not eligible:
        limitations.append("No player-match rows with positive minutes are available for this fixture side.")
    if limitation:
        limitations.append(limitation)
    return FixturePlayerPerformance(side=side, team_name=team_name, metrics=metrics, status=status, limitations=limitations)


def install(app: FastAPI) -> None:
    @app.get(
        "/api/v1/fixtures/{season}/{fixture_id}/player-performance",
        response_model=FixturePlayerPerformanceResponse,
    )
    def get_fixture_player_performance(season: str, fixture_id: str) -> FixturePlayerPerformanceResponse:
        try:
            detail = query_api.fixture_detail(season=season, fixture_id=fixture_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail="Fixture player performance failed safely.") from exc

        fixture = detail["fixture"]
        limitation: str | None = None
        try:
            rows = player_match_stats.fixture_player_match_rows(fixture)
        except FileNotFoundError as exc:
            rows = tuple()
            limitation = f"Player-match evidence source unavailable: {exc}"
        except ValueError as exc:
            rows = tuple()
            limitation = f"Player-match evidence could not be reconciled safely: {exc}"

        return FixturePlayerPerformanceResponse(
            season=season,
            fixture_id=fixture_id,
            home=_side_payload(rows, "home", str(fixture["home_team_name"]), limitation),
            away=_side_payload(rows, "away", str(fixture["away_team_name"]), limitation),
        )
