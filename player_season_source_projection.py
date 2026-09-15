"""Governed source-native Player-Season projection for player analysis.

The packaged CSV preserves source Player-Season rows. Runtime attachment uses
only verified identity relationships already held by FRL:

* a direct FPL player-code == Player-Season playerId edge where present; or
* historical FPL element -> Player-Match playerId -> PulseLive ``pl_code``.

The second edge is represented by the existing rich player projection, whose
``source_player_id`` and ``player_code`` columns retain those two source IDs.
No player-name matching is performed at runtime. Missing values and unresolved
identity edges remain unavailable.
"""
from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path

import rich_player_projection


ROOT = Path(__file__).resolve().parent
PACKAGED = ROOT / "data" / "player_season_source_stats_v1.csv"
METADATA = ROOT / "data" / "player_season_source_stats_v1.metadata.json"
IDENTITY_REGISTRY = ROOT / "player_identity_registry.csv"

SOURCE_METRICS = {
    "forward_passes": "forwardPasses",
}


def _number_or_none(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def _packaged_rows() -> tuple[dict[str, str], ...]:
    if not PACKAGED.is_file():
        return tuple()
    with PACKAGED.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(dict(row) for row in csv.DictReader(handle))


@lru_cache(maxsize=1)
def projection_metadata() -> dict:
    if not METADATA.is_file():
        return {}
    return json.loads(METADATA.read_text(encoding="utf-8"))


@lru_cache(maxsize=20)
def season_totals_by_source_player_id(
    season: str,
) -> dict[str, dict[str, float | None]]:
    output: dict[str, dict[str, float | None]] = {}
    for row in _packaged_rows():
        if str(row.get("season") or "").strip() != season:
            continue
        source_player_id = str(
            row.get("source_player_id") or ""
        ).strip()
        if not source_player_id:
            continue
        output[source_player_id] = {
            metric: _number_or_none(row.get(metric))
            for metric in SOURCE_METRICS
        }
    return output


@lru_cache(maxsize=20)
def _historical_element_to_player_match_id(
    season: str,
) -> dict[str, str]:
    if not IDENTITY_REGISTRY.is_file():
        return {}

    candidates: dict[str, set[str]] = {}
    with IDENTITY_REGISTRY.open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            if str(row.get("season") or "").strip() != season:
                continue
            if str(row.get("identity_status") or "").strip() != "VERIFIED":
                continue
            element = str(row.get("fpl_element") or "").strip()
            source_player_id = str(
                row.get("source_player_id") or ""
            ).strip()
            if element and source_player_id:
                candidates.setdefault(element, set()).add(source_player_id)

    return {
        element: next(iter(source_ids))
        for element, source_ids in candidates.items()
        if len(source_ids) == 1
    }


@lru_cache(maxsize=20)
def _player_match_to_player_season_id(
    season: str,
) -> dict[str, str]:
    return rich_player_projection.pulselive_code_by_player_match_source_id(
        season
    )


def source_player_id_for_profile(
    season: str,
    profile_player_code: str,
) -> tuple[str | None, str]:
    """Resolve a profile ID to Player-Season identity without names."""
    profile_player_code = str(profile_player_code or "").strip()
    source_rows = season_totals_by_source_player_id(season)

    if profile_player_code in source_rows:
        return profile_player_code, "FPL_PLAYER_CODE_TO_PLAYER_SEASON_PLAYER_ID_EXACT"

    player_match_id = _historical_element_to_player_match_id(
        season
    ).get(profile_player_code)
    if player_match_id is None:
        return None, "UNRESOLVED"

    player_season_id = _player_match_to_player_season_id(
        season
    ).get(player_match_id)
    if player_season_id not in source_rows:
        return None, "UNRESOLVED"

    return (
        player_season_id,
        "FPL_ELEMENT_TO_VERIFIED_PLAYER_MATCH_ID_TO_PLAYER_SEASON_PLAYER_ID",
    )


def enrich_player(player: dict, season: str) -> dict:
    """Attach governed Player-Season values to one player research record."""
    enriched = dict(player)
    profile_player_code = str(player.get("player_code") or "").strip()
    source_player_id, identity_route = source_player_id_for_profile(
        season,
        profile_player_code,
    )

    if source_player_id is None:
        for metric in SOURCE_METRICS:
            enriched.setdefault(metric, None)
        enriched["_player_season_source_projection"] = "UNAVAILABLE"
        enriched["_player_season_identity_route"] = identity_route
        return enriched

    totals = season_totals_by_source_player_id(season)[source_player_id]
    enriched.update(totals)
    enriched["_player_season_source_projection"] = (
        "PLAYER_SEASON_SOURCE_STATS_V1"
    )
    enriched["_player_season_source_player_id"] = source_player_id
    enriched["_player_season_identity_route"] = identity_route
    return enriched


def clear_caches() -> None:
    _packaged_rows.cache_clear()
    projection_metadata.cache_clear()
    season_totals_by_source_player_id.cache_clear()
    _historical_element_to_player_match_id.cache_clear()
    _player_match_to_player_season_id.cache_clear()


__all__ = [
    "IDENTITY_REGISTRY",
    "METADATA",
    "PACKAGED",
    "SOURCE_METRICS",
    "clear_caches",
    "enrich_player",
    "projection_metadata",
    "season_totals_by_source_player_id",
    "source_player_id_for_profile",
]
