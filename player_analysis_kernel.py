from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Iterable

import player_research


COMPETITION_RANK = "COMPETITION_RANK"
RANK_POSITION_PERCENTILE = "RANK_POSITION_PERCENTILE"
ANALYSIS_VERSION = "player-analysis-kernel-v3"
PLAYER_SEASON_AGGREGATE = "PLAYER_SEASON_AGGREGATE"
PLAYER_SEASON_DERIVATION = "PLAYER_SEASON_DERIVATION"

RAW = "RAW"
PER_90 = "PER_90"
RATE = "RATE"

POSITIONS = ("GKP", "DEF", "MID", "FWD")
FAMILIES = (
    "overview",
    "shooting",
    "creation",
    "possession",
    "defending",
    "discipline",
    "goalkeeping",
    "fpl",
)


@dataclass(frozen=True)
class MetricDefinition:
    key: str
    concept_key: str
    normalization: str
    label: str
    unit: str
    family: str
    higher_is_better: bool
    positions: tuple[str, ...]
    representation: str
    source_key: str | None = None
    numerator_key: str | None = None
    denominator_key: str | None = None
    per_90: bool = False


OUTFIELD = ("DEF", "MID", "FWD")
ALL_POSITIONS = POSITIONS


def _total(key: str, label: str, unit: str, family: str, *, higher_is_better: bool = True, positions: tuple[str, ...] = ALL_POSITIONS) -> MetricDefinition:
    return MetricDefinition(
        key=key,
        concept_key=key,
        normalization=RAW,
        label=label,
        unit=unit,
        family=family,
        higher_is_better=higher_is_better,
        positions=positions,
        representation=PLAYER_SEASON_AGGREGATE,
        source_key=key,
    )


def _per90(key: str, source_key: str, label: str, unit: str, family: str, *, higher_is_better: bool = True, positions: tuple[str, ...] = ALL_POSITIONS) -> MetricDefinition:
    return MetricDefinition(
        key=key,
        concept_key=source_key,
        normalization=PER_90,
        label=label,
        unit=unit,
        family=family,
        higher_is_better=higher_is_better,
        positions=positions,
        representation=PLAYER_SEASON_DERIVATION,
        source_key=source_key,
        per_90=True,
    )


def _rate(key: str, label: str, family: str, numerator: str, denominator: str, *, higher_is_better: bool = True, positions: tuple[str, ...] = ALL_POSITIONS) -> MetricDefinition:
    return MetricDefinition(
        key=key,
        concept_key=key,
        normalization=RATE,
        label=label,
        unit="%",
        family=family,
        higher_is_better=higher_is_better,
        positions=positions,
        representation=PLAYER_SEASON_DERIVATION,
        numerator_key=numerator,
        denominator_key=denominator,
    )


METRIC_DEFINITIONS = (
    # Shooting / output.
    _total("goals", "Goals", "goals", "shooting", positions=OUTFIELD),
    _per90("goals_per_90", "goals", "Goals / 90", "goals", "shooting", positions=OUTFIELD),
    _total("xg", "xG", "xG", "shooting", positions=OUTFIELD),
    _per90("xg_per_90", "xg", "xG / 90", "xG", "shooting", positions=OUTFIELD),
    _total("shots", "Shots", "shots", "shooting", positions=OUTFIELD),
    _per90("shots_per_90", "shots", "Shots / 90", "shots", "shooting", positions=OUTFIELD),
    _total("shots_on_target", "Shots on target", "shots", "shooting", positions=OUTFIELD),
    _per90("shots_on_target_per_90", "shots_on_target", "Shots on target / 90", "shots", "shooting", positions=OUTFIELD),
    _total("shots_off_target", "Shots off target", "shots", "shooting", positions=OUTFIELD),
    _per90("shots_off_target_per_90", "shots_off_target", "Shots off target / 90", "shots", "shooting", positions=OUTFIELD),
    _total("blocked_shots", "Blocked shots", "shots", "shooting", positions=OUTFIELD),
    _per90("blocked_shots_per_90", "blocked_shots", "Blocked shots / 90", "shots", "shooting", positions=OUTFIELD),
    _total("xgot", "xGOT", "xGOT", "shooting", positions=OUTFIELD),
    _per90("xgot_per_90", "xgot", "xGOT / 90", "xGOT", "shooting", positions=OUTFIELD),
    _total("hit_woodwork", "Hit woodwork", "shots", "shooting", positions=OUTFIELD),
    _per90("hit_woodwork_per_90", "hit_woodwork", "Woodwork / 90", "shots", "shooting", positions=OUTFIELD),
    _total("penalties_missed", "Penalties missed", "penalties", "shooting", higher_is_better=False, positions=OUTFIELD),
    # Creation.
    _total("assists", "Assists", "assists", "creation", positions=OUTFIELD),
    _per90("assists_per_90", "assists", "Assists / 90", "assists", "creation", positions=OUTFIELD),
    _total("xa", "xA", "xA", "creation", positions=OUTFIELD),
    _per90("xa_per_90", "xa", "xA / 90", "xA", "creation", positions=OUTFIELD),
    _total("xgi", "xGI", "xGI", "creation", positions=OUTFIELD),
    _per90("xgi_per_90", "xgi", "xGI / 90", "xGI", "creation", positions=OUTFIELD),
    _total("key_passes", "Key passes", "passes", "creation", positions=OUTFIELD),
    _per90("key_passes_per_90", "key_passes", "Key passes / 90", "passes", "creation", positions=OUTFIELD),
    _total("big_chances_created", "Big chances created", "chances", "creation", positions=OUTFIELD),
    _per90("big_chances_created_per_90", "big_chances_created", "Big chances created / 90", "chances", "creation", positions=OUTFIELD),
    _total("crosses", "Open-play crosses", "crosses", "creation", positions=OUTFIELD),
    _per90("crosses_per_90", "crosses", "Open-play crosses / 90", "crosses", "creation", positions=OUTFIELD),
    _total("successful_crosses", "Successful crosses", "crosses", "creation", positions=OUTFIELD),
    _per90("successful_crosses_per_90", "successful_crosses", "Successful crosses / 90", "crosses", "creation", positions=OUTFIELD),
    _total("accurate_opposition_half_passes", "Accurate passes in opposition half", "passes", "creation", positions=OUTFIELD),
    _per90("accurate_opposition_half_passes_per_90", "accurate_opposition_half_passes", "Accurate opposition-half passes / 90", "passes", "creation", positions=OUTFIELD),
    # Possession / ball use.
    _total("attempted_passes", "Attempted passes", "passes", "possession"),
    _per90("attempted_passes_per_90", "attempted_passes", "Attempted passes / 90", "passes", "possession"),
    _total("completed_passes", "Completed passes", "passes", "possession"),
    _per90("completed_passes_per_90", "completed_passes", "Completed passes / 90", "passes", "possession"),
    _rate("pass_completion", "Pass completion", "possession", "completed_passes", "attempted_passes"),
    _total("passes", "Passes", "passes", "possession"),
    _per90("passes_per_90", "passes", "Passes / 90", "passes", "possession"),
    _total("accurate_passes", "Accurate passes", "passes", "possession"),
    _per90("accurate_passes_per_90", "accurate_passes", "Accurate passes / 90", "passes", "possession"),
    _rate("rich_pass_accuracy", "Pass accuracy", "possession", "accurate_passes", "passes"),
    _total("long_balls", "Long balls", "passes", "possession"),
    _per90("long_balls_per_90", "long_balls", "Long balls / 90", "passes", "possession"),
    _total("accurate_long_balls", "Accurate long balls", "passes", "possession"),
    _per90("accurate_long_balls_per_90", "accurate_long_balls", "Accurate long balls / 90", "passes", "possession"),
    _rate("long_ball_accuracy", "Long-ball accuracy", "possession", "accurate_long_balls", "long_balls"),
    _total("touches", "Touches", "touches", "possession", positions=OUTFIELD),
    _per90("touches_per_90", "touches", "Touches / 90", "touches", "possession", positions=OUTFIELD),
    _total("dribbles", "Dribbles", "dribbles", "possession", positions=OUTFIELD),
    _per90("dribbles_per_90", "dribbles", "Dribbles / 90", "dribbles", "possession", positions=OUTFIELD),
    _total("successful_dribbles", "Successful dribbles", "dribbles", "possession", positions=OUTFIELD),
    _per90("successful_dribbles_per_90", "successful_dribbles", "Successful dribbles / 90", "dribbles", "possession", positions=OUTFIELD),
    _total("unsuccessful_dribbles", "Unsuccessful dribbles", "dribbles", "possession", higher_is_better=False, positions=OUTFIELD),
    _per90("unsuccessful_dribbles_per_90", "unsuccessful_dribbles", "Unsuccessful dribbles / 90", "dribbles", "possession", higher_is_better=False, positions=OUTFIELD),
    _total("ball_carries", "Ball carries", "carries", "possession", positions=OUTFIELD),
    _per90("ball_carries_per_90", "ball_carries", "Ball carries / 90", "carries", "possession", positions=OUTFIELD),
    _total("progressive_carries", "Progressive carries", "carries", "possession", positions=OUTFIELD),
    _per90("progressive_carries_per_90", "progressive_carries", "Progressive carries / 90", "carries", "possession", positions=OUTFIELD),
    _total("progressive_carry_distance", "Progressive carry distance", "distance", "possession", positions=OUTFIELD),
    _per90("progressive_carry_distance_per_90", "progressive_carry_distance", "Progressive carry distance / 90", "distance", "possession", positions=OUTFIELD),
    _total("total_progression", "Total progression", "progression", "possession", positions=OUTFIELD),
    _per90("total_progression_per_90", "total_progression", "Total progression / 90", "progression", "possession", positions=OUTFIELD),
    _total("possession_lost", "Possession lost", "events", "possession", higher_is_better=False, positions=OUTFIELD),
    _per90("possession_lost_per_90", "possession_lost", "Possession lost / 90", "events", "possession", higher_is_better=False, positions=OUTFIELD),
    # Defending / duels.
    _total("tackles", "Tackles", "tackles", "defending"),
    _per90("tackles_per_90", "tackles", "Tackles / 90", "tackles", "defending"),
    _total("tackles_won", "Tackles won", "tackles", "defending", positions=OUTFIELD),
    _per90("tackles_won_per_90", "tackles_won", "Tackles won / 90", "tackles", "defending", positions=OUTFIELD),
    _total("interceptions_won", "Interceptions", "interceptions", "defending", positions=OUTFIELD),
    _per90("interceptions_won_per_90", "interceptions_won", "Interceptions / 90", "interceptions", "defending", positions=OUTFIELD),
    _total("clearances", "Clearances", "clearances", "defending", positions=OUTFIELD),
    _per90("clearances_per_90", "clearances", "Clearances / 90", "clearances", "defending", positions=OUTFIELD),
    _total("blocks", "Blocks", "blocks", "defending", positions=OUTFIELD),
    _per90("blocks_per_90", "blocks", "Blocks / 90", "blocks", "defending", positions=OUTFIELD),
    _total("recoveries", "Recoveries", "recoveries", "defending"),
    _per90("recoveries_per_90", "recoveries", "Recoveries / 90", "recoveries", "defending"),
    _total("aerial_duels_won", "Aerial duels won", "duels", "defending", positions=OUTFIELD),
    _per90("aerial_duels_won_per_90", "aerial_duels_won", "Aerial duels won / 90", "duels", "defending", positions=OUTFIELD),
    _total("aerial_duels_lost", "Aerial duels lost", "duels", "defending", higher_is_better=False, positions=OUTFIELD),
    _per90("aerial_duels_lost_per_90", "aerial_duels_lost", "Aerial duels lost / 90", "duels", "defending", higher_is_better=False, positions=OUTFIELD),
    _total("duels_won", "Duels won", "duels", "defending", positions=OUTFIELD),
    _per90("duels_won_per_90", "duels_won", "Duels won / 90", "duels", "defending", positions=OUTFIELD),
    _total("duels_lost", "Duels lost", "duels", "defending", higher_is_better=False, positions=OUTFIELD),
    _per90("duels_lost_per_90", "duels_lost", "Duels lost / 90", "duels", "defending", higher_is_better=False, positions=OUTFIELD),
    _total("contests_won", "Contests won", "duels", "defending", positions=OUTFIELD),
    _per90("contests_won_per_90", "contests_won", "Contests won / 90", "duels", "defending", positions=OUTFIELD),
    _total("errors_leading_to_shot", "Errors leading to shot", "errors", "defending", higher_is_better=False, positions=OUTFIELD),
    _total("errors_leading_to_goal", "Errors leading to goal", "errors", "defending", higher_is_better=False, positions=OUTFIELD),
    _total("cbi", "Clearances, blocks & interceptions", "actions", "defending"),
    _per90("cbi_per_90", "cbi", "CBI / 90", "actions", "defending"),
    _total("defensive_contribution", "Defensive contribution", "actions", "defending"),
    _per90("defensive_contribution_per_90", "defensive_contribution", "Defensive contribution / 90", "actions", "defending"),
    _total("clean_sheets", "Clean sheets", "clean sheets", "defending", positions=("GKP", "DEF")),
    _per90("clean_sheets_per_90", "clean_sheets", "Clean sheets / 90", "clean sheets", "defending", positions=("GKP", "DEF")),
    # Discipline.
    _total("fouls_won", "Fouls won", "fouls", "discipline", positions=OUTFIELD),
    _per90("fouls_won_per_90", "fouls_won", "Fouls won / 90", "fouls", "discipline", positions=OUTFIELD),
    _total("fouls_conceded", "Fouls conceded", "fouls", "discipline", higher_is_better=False, positions=OUTFIELD),
    _per90("fouls_conceded_per_90", "fouls_conceded", "Fouls conceded / 90", "fouls", "discipline", higher_is_better=False, positions=OUTFIELD),
    _total("penalties_won", "Penalties won", "penalties", "discipline", positions=OUTFIELD),
    _total("penalties_conceded", "Penalties conceded", "penalties", "discipline", higher_is_better=False, positions=OUTFIELD),
    _total("yellow_cards", "Yellow cards", "cards", "discipline", higher_is_better=False),
    _per90("yellow_cards_per_90", "yellow_cards", "Yellow cards / 90", "cards", "discipline", higher_is_better=False),
    _total("red_cards", "Red cards", "cards", "discipline", higher_is_better=False),
    _per90("red_cards_per_90", "red_cards", "Red cards / 90", "cards", "discipline", higher_is_better=False),
    _total("own_goals", "Own goals", "goals", "discipline", higher_is_better=False),
    # Goalkeeping.
    _total("saves", "Saves", "saves", "goalkeeping", positions=("GKP",)),
    _per90("saves_per_90", "saves", "Saves / 90", "saves", "goalkeeping", positions=("GKP",)),
    _total("saves_inside_box", "Saves inside box", "saves", "goalkeeping", positions=("GKP",)),
    _per90("saves_inside_box_per_90", "saves_inside_box", "Saves inside box / 90", "saves", "goalkeeping", positions=("GKP",)),
    _total("high_claims", "High claims", "claims", "goalkeeping", positions=("GKP",)),
    _per90("high_claims_per_90", "high_claims", "High claims / 90", "claims", "goalkeeping", positions=("GKP",)),
    _total("keeper_sweeper_actions", "Keeper sweeper actions", "actions", "goalkeeping", positions=("GKP",)),
    _per90("keeper_sweeper_actions_per_90", "keeper_sweeper_actions", "Keeper sweeper actions / 90", "actions", "goalkeeping", positions=("GKP",)),
    _total("accurate_keeper_sweeper_actions", "Accurate keeper sweeper actions", "actions", "goalkeeping", positions=("GKP",)),
    _rate("keeper_sweeper_accuracy", "Keeper sweeper accuracy", "goalkeeping", "accurate_keeper_sweeper_actions", "keeper_sweeper_actions", positions=("GKP",)),
    _total("penalties_faced", "Penalties faced", "penalties", "goalkeeping", positions=("GKP",)),
    _per90("goals_conceded_per_90", "goals_conceded", "Goals conceded / 90", "goals", "goalkeeping", higher_is_better=False, positions=("GKP",)),
    _total("xgc", "xGC", "xGC", "goalkeeping", higher_is_better=False, positions=("GKP",)),
    _per90("xgc_per_90", "xgc", "xGC / 90", "xGC", "goalkeeping", higher_is_better=False, positions=("GKP",)),
    _total("penalties_saved", "Penalties saved", "penalties", "goalkeeping", positions=("GKP",)),
    # FPL-native context.
    _total("points", "FPL points", "points", "fpl"),
    _per90("points_per_90", "points", "FPL points / 90", "points", "fpl"),
    _total("bonus", "FPL bonus", "bonus", "fpl"),
    _total("bps", "BPS", "BPS", "fpl"),
    _per90("bps_per_90", "bps", "BPS / 90", "BPS", "fpl"),
    _total("ict_influence", "ICT influence", "index", "fpl"),
    _total("ict_creativity", "ICT creativity", "index", "fpl"),
    _total("ict_threat", "ICT threat", "index", "fpl"),
    _total("ict_index", "ICT index", "index", "fpl"),
)

DEFINITIONS_BY_KEY = {definition.key: definition for definition in METRIC_DEFINITIONS}


def _normalizations_by_concept() -> dict[str, tuple[str, ...]]:
    normalizations: dict[str, list[str]] = {}
    for definition in METRIC_DEFINITIONS:
        values = normalizations.setdefault(definition.concept_key, [])
        if definition.normalization not in values:
            values.append(definition.normalization)
    return {key: tuple(values) for key, values in normalizations.items()}


NORMALIZATIONS_BY_CONCEPT = _normalizations_by_concept()


def definition_payload(definition: MetricDefinition) -> dict:
    return {
        **asdict(definition),
        "supported_normalizations": list(
            NORMALIZATIONS_BY_CONCEPT.get(definition.concept_key, (definition.normalization,))
        ),
    }


OVERVIEW_KEYS_BY_POSITION = {
    "GKP": (
        "saves_per_90",
        "saves_inside_box_per_90",
        "high_claims_per_90",
        "clean_sheets_per_90",
        "goals_conceded_per_90",
        "xgc_per_90",
        "penalties_saved",
        "bps_per_90",
    ),
    "DEF": (
        "goals_per_90",
        "assists_per_90",
        "tackles_won_per_90",
        "interceptions_won_per_90",
        "clearances_per_90",
        "duels_won_per_90",
        "recoveries_per_90",
        "clean_sheets_per_90",
    ),
    "MID": (
        "goals_per_90",
        "assists_per_90",
        "shots_per_90",
        "key_passes_per_90",
        "successful_dribbles_per_90",
        "progressive_carries_per_90",
        "duels_won_per_90",
        "recoveries_per_90",
    ),
    "FWD": (
        "goals_per_90",
        "assists_per_90",
        "shots_per_90",
        "shots_on_target_per_90",
        "xgot_per_90",
        "key_passes_per_90",
        "successful_dribbles_per_90",
        "progressive_carries_per_90",
    ),
}


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def metric_value(player: dict, definition: MetricDefinition) -> float | None:
    if definition.numerator_key and definition.denominator_key:
        numerator = _number(player.get(definition.numerator_key))
        denominator = _number(player.get(definition.denominator_key))
        if numerator is None or denominator in (None, 0):
            return None
        return numerator / denominator * 100.0
    if definition.source_key is None:
        return None
    value = _number(player.get(definition.source_key))
    if value is None:
        return None
    if definition.per_90:
        minutes = _number(player.get("minutes"))
        if minutes in (None, 0):
            return None
        return value / minutes * 90.0
    return value


def rank_metric_entries(entries: list[dict], higher_is_better: bool) -> list[dict]:
    available = [entry for entry in entries if entry.get("value") is not None]
    out_of = len(available)
    for entry in entries:
        value = entry.get("value")
        if value is None:
            entry["rank"] = None
            entry["out_of"] = out_of
            entry["percentile"] = None
            continue
        numeric = float(value)
        better = sum(
            1 for candidate in available
            if (float(candidate["value"]) > numeric if higher_is_better else float(candidate["value"]) < numeric)
        )
        rank = better + 1
        entry["rank"] = rank
        entry["out_of"] = out_of
        entry["percentile"] = 100.0 if out_of == 1 else round(100.0 * (out_of - rank) / (out_of - 1), 1)
    return entries


def _public_identity(player: dict) -> dict:
    return {
        "player_code": str(player.get("player_code") or ""),
        "player_name": str(player.get("player_name") or ""),
        "position": str(player.get("position") or ""),
        "clubs": list(player.get("clubs") or ()),
        "minutes": int(float(player.get("minutes") or 0)),
        "starts": int(float(player.get("starts") or 0)),
        "appearances": int(player.get("appearances") or 0),
    }


def _position_population(season: str, position: str) -> list[dict]:
    if position not in POSITIONS:
        raise ValueError(f"Unsupported player position: {position}")
    return [
        player for player in player_research.season_players(season)
        if str(player.get("position") or "") == position and float(player.get("minutes") or 0) > 0
    ]


def _definitions_for_position(position: str) -> Iterable[MetricDefinition]:
    return (definition for definition in METRIC_DEFINITIONS if position in definition.positions)


@lru_cache(maxsize=64)
def season_position_analysis(season: str, position: str) -> dict:
    if season not in set(player_research.available_seasons()):
        raise ValueError(f"Unsupported player season: {season}")
    population = _position_population(season, position)
    metrics: dict[str, dict] = {}
    for definition in _definitions_for_position(position):
        entries = [
            {**_public_identity(player), "value": metric_value(player, definition)}
            for player in population
        ]
        rank_metric_entries(entries, definition.higher_is_better)
        observed = sum(entry["value"] is not None for entry in entries)
        metrics[definition.key] = {
            "definition": definition_payload(definition),
            "entries": entries,
            "observed_players": observed,
            "eligible_players": len(entries),
            "availability": (
                "AVAILABLE" if observed == len(entries) and entries
                else "PARTIAL" if observed
                else "UNAVAILABLE"
            ),
            "ranking_policy": COMPETITION_RANK,
            "percentile_policy": RANK_POSITION_PERCENTILE,
        }
    return {
        "analysis_version": ANALYSIS_VERSION,
        "season": season,
        "position": position,
        "population_size": len(population),
        "cohort": {
            "competition": "Premier League",
            "season": season,
            "position": position,
            "minimum_minutes": 1,
            "description": f"Premier League {position} players with at least 1 recorded minute in {season}",
        },
        "ranking_policy": COMPETITION_RANK,
        "percentile_policy": RANK_POSITION_PERCENTILE,
        "metrics": metrics,
    }


def player_analysis(season: str, player_code: str) -> dict | None:
    player = player_research.player_detail(season, player_code)
    if player is None:
        return None
    position = str(player.get("position") or "")
    if position not in POSITIONS:
        return None
    season_analysis = season_position_analysis(season, position)
    selected_metrics: list[dict] = []
    for key, metric in season_analysis["metrics"].items():
        definition = metric["definition"]
        entry = next(
            (candidate for candidate in metric["entries"] if candidate["player_code"] == str(player_code)),
            None,
        )
        if entry is None:
            continue
        selected_metrics.append(
            {
                **definition,
                **entry,
                "availability": metric["availability"],
                "observed_players": metric["observed_players"],
                "eligible_players": metric["eligible_players"],
                "ranking_policy": metric["ranking_policy"],
                "percentile_policy": metric["percentile_policy"],
            }
        )
    overview_keys = OVERVIEW_KEYS_BY_POSITION[position]
    return {
        "analysis_version": ANALYSIS_VERSION,
        "season": season,
        "player": _public_identity(player),
        "cohort": season_analysis["cohort"],
        "overview_keys": list(overview_keys),
        "metrics": selected_metrics,
    }


__all__ = [
    "ANALYSIS_VERSION",
    "COMPETITION_RANK",
    "DEFINITIONS_BY_KEY",
    "FAMILIES",
    "METRIC_DEFINITIONS",
    "NORMALIZATIONS_BY_CONCEPT",
    "OVERVIEW_KEYS_BY_POSITION",
    "PER_90",
    "PLAYER_SEASON_AGGREGATE",
    "PLAYER_SEASON_DERIVATION",
    "POSITIONS",
    "RANK_POSITION_PERCENTILE",
    "RATE",
    "RAW",
    "MetricDefinition",
    "definition_payload",
    "metric_value",
    "player_analysis",
    "rank_metric_entries",
    "season_position_analysis",
]
