from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Iterable

import player_research


COMPETITION_RANK = "COMPETITION_RANK"
RANK_POSITION_PERCENTILE = "RANK_POSITION_PERCENTILE"
ANALYSIS_VERSION = "player-analysis-kernel-v2"
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


def _total(
    key: str,
    label: str,
    unit: str,
    family: str,
    *,
    higher_is_better: bool = True,
    positions: tuple[str, ...] = ALL_POSITIONS,
) -> MetricDefinition:
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


def _per90(
    key: str,
    source_key: str,
    label: str,
    unit: str,
    family: str,
    *,
    higher_is_better: bool = True,
    positions: tuple[str, ...] = ALL_POSITIONS,
) -> MetricDefinition:
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


METRIC_DEFINITIONS = (
    # Shooting / output.
    _total("goals", "Goals", "goals", "shooting", positions=OUTFIELD),
    _per90("goals_per_90", "goals", "Goals / 90", "goals", "shooting", positions=OUTFIELD),
    _total("xg", "xG", "xG", "shooting", positions=OUTFIELD),
    _per90("xg_per_90", "xg", "xG / 90", "xG", "shooting", positions=OUTFIELD),
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
    # Possession / ball use. These remain absent in seasons whose player source
    # does not expose the underlying representation.
    _total("attempted_passes", "Attempted passes", "passes", "possession"),
    _per90("attempted_passes_per_90", "attempted_passes", "Attempted passes / 90", "passes", "possession"),
    _total("completed_passes", "Completed passes", "passes", "possession"),
    _per90("completed_passes_per_90", "completed_passes", "Completed passes / 90", "passes", "possession"),
    MetricDefinition(
        key="pass_completion",
        concept_key="pass_completion",
        normalization=RATE,
        label="Pass completion",
        unit="%",
        family="possession",
        higher_is_better=True,
        positions=ALL_POSITIONS,
        representation=PLAYER_SEASON_DERIVATION,
        numerator_key="completed_passes",
        denominator_key="attempted_passes",
    ),
    _total("dribbles", "Dribbles", "dribbles", "possession", positions=OUTFIELD),
    _per90("dribbles_per_90", "dribbles", "Dribbles / 90", "dribbles", "possession", positions=OUTFIELD),
    # Defending.
    _total("tackles", "Tackles", "tackles", "defending"),
    _per90("tackles_per_90", "tackles", "Tackles / 90", "tackles", "defending"),
    _total("recoveries", "Recoveries", "recoveries", "defending"),
    _per90("recoveries_per_90", "recoveries", "Recoveries / 90", "recoveries", "defending"),
    _total("cbi", "Clearances, blocks & interceptions", "actions", "defending"),
    _per90("cbi_per_90", "cbi", "CBI / 90", "actions", "defending"),
    _total("defensive_contribution", "Defensive contribution", "actions", "defending"),
    _per90("defensive_contribution_per_90", "defensive_contribution", "Defensive contribution / 90", "actions", "defending"),
    _total("clean_sheets", "Clean sheets", "clean sheets", "defending", positions=("GKP", "DEF")),
    _per90("clean_sheets_per_90", "clean_sheets", "Clean sheets / 90", "clean sheets", "defending", positions=("GKP", "DEF")),
    # Discipline.
    _total("yellow_cards", "Yellow cards", "cards", "discipline", higher_is_better=False),
    _per90("yellow_cards_per_90", "yellow_cards", "Yellow cards / 90", "cards", "discipline", higher_is_better=False),
    _total("red_cards", "Red cards", "cards", "discipline", higher_is_better=False),
    _per90("red_cards_per_90", "red_cards", "Red cards / 90", "cards", "discipline", higher_is_better=False),
    _total("own_goals", "Own goals", "goals", "discipline", higher_is_better=False),
    # Goalkeeping.
    _total("saves", "Saves", "saves", "goalkeeping", positions=("GKP",)),
    _per90("saves_per_90", "saves", "Saves / 90", "saves", "goalkeeping", positions=("GKP",)),
    _per90("goals_conceded_per_90", "goals_conceded", "Goals conceded / 90", "goals", "goalkeeping", higher_is_better=False, positions=("GKP",)),
    _total("xgc", "xGC", "xGC", "goalkeeping", higher_is_better=False, positions=("GKP",)),
    _per90("xgc_per_90", "xgc", "xGC / 90", "xGC", "goalkeeping", higher_is_better=False, positions=("GKP",)),
    _total("penalties_saved", "Penalties saved", "penalties", "goalkeeping", positions=("GKP",)),
    # FPL-native context. These are labelled separately in product copy and are
    # never promoted to generic football-statistic equivalence.
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
            NORMALIZATIONS_BY_CONCEPT.get(
                definition.concept_key,
                (definition.normalization,),
            )
        ),
    }


OVERVIEW_KEYS_BY_POSITION = {
    "GKP": (
        "saves_per_90",
        "clean_sheets_per_90",
        "goals_conceded_per_90",
        "xgc_per_90",
        "penalties_saved",
        "bps_per_90",
    ),
    "DEF": (
        "goals_per_90",
        "assists_per_90",
        "xgi_per_90",
        "tackles_per_90",
        "recoveries_per_90",
        "defensive_contribution_per_90",
        "cbi_per_90",
        "clean_sheets_per_90",
    ),
    "MID": (
        "goals_per_90",
        "assists_per_90",
        "xg_per_90",
        "xa_per_90",
        "xgi_per_90",
        "key_passes_per_90",
        "tackles_per_90",
        "recoveries_per_90",
    ),
    "FWD": (
        "goals_per_90",
        "assists_per_90",
        "xg_per_90",
        "xa_per_90",
        "xgi_per_90",
        "key_passes_per_90",
        "big_chances_created_per_90",
        "dribbles_per_90",
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
            1
            for candidate in available
            if (
                float(candidate["value"]) > numeric
                if higher_is_better
                else float(candidate["value"]) < numeric
            )
        )
        rank = better + 1
        entry["rank"] = rank
        entry["out_of"] = out_of
        entry["percentile"] = (
            100.0
            if out_of == 1
            else round(100.0 * (out_of - rank) / (out_of - 1), 1)
        )

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
        player
        for player in player_research.season_players(season)
        if str(player.get("position") or "") == position
        and float(player.get("minutes") or 0) > 0
    ]


def _definitions_for_position(position: str) -> Iterable[MetricDefinition]:
    return (
        definition
        for definition in METRIC_DEFINITIONS
        if position in definition.positions
    )


@lru_cache(maxsize=64)
def season_position_analysis(season: str, position: str) -> dict:
    if season not in set(player_research.available_seasons()):
        raise ValueError(f"Unsupported player season: {season}")

    population = _position_population(season, position)
    metrics: dict[str, dict] = {}

    for definition in _definitions_for_position(position):
        entries = []
        for player in population:
            entries.append(
                {
                    **_public_identity(player),
                    "value": metric_value(player, definition),
                }
            )

        rank_metric_entries(entries, definition.higher_is_better)
        observed = sum(entry["value"] is not None for entry in entries)
        metrics[definition.key] = {
            "definition": definition_payload(definition),
            "entries": entries,
            "observed_players": observed,
            "eligible_players": len(entries),
            "availability": (
                "AVAILABLE"
                if observed == len(entries) and entries
                else "PARTIAL"
                if observed
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
            (
                candidate
                for candidate in metric["entries"]
                if candidate["player_code"] == str(player_code)
            ),
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
