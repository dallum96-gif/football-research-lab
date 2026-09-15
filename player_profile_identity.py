"""Governed cross-source identity seam for Player Profile.

A Player Profile route uses a season-specific FPL identity. That route id is
not treated as a longitudinal player id. This module resolves it through
tracked, verified FRL relationship evidence to a reusable research identity
key, and exposes source-specific ids separately for downstream consumers.

No player-name matching is used to establish cross-season continuity.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

import player_research
import rich_player_projection


ROOT = Path(__file__).resolve().parent
CURRENT_RELATIONSHIPS = ROOT / "data" / "fpl_player_identity_relationships.csv"
HISTORICAL_REGISTRY = ROOT / "player_identity_registry.csv"
VERIFIED_STATUSES = frozenset({"VERIFIED", "SOURCE_NATIVE_VERIFIED"})


def _text(value: object) -> str:
    return str(value or "").strip()


def _read(path: Path) -> tuple[dict[str, str], ...]:
    if not path.is_file():
        return tuple()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(dict(row) for row in csv.DictReader(handle))


@lru_cache(maxsize=1)
def _current_rows() -> tuple[dict[str, str], ...]:
    return _read(CURRENT_RELATIONSHIPS)


@lru_cache(maxsize=1)
def _historical_rows() -> tuple[dict[str, str], ...]:
    return _read(HISTORICAL_REGISTRY)


@lru_cache(maxsize=1)
def _current_indexes() -> tuple[
    dict[tuple[str, str], tuple[dict[str, str], ...]],
    dict[tuple[str, str], tuple[dict[str, str], ...]],
]:
    by_element: dict[tuple[str, str], list[dict[str, str]]] = {}
    by_code: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in _current_rows():
        if _text(row.get("identity_status")).upper() not in VERIFIED_STATUSES:
            continue
        if _text(row.get("candidate_count")) not in {"", "1"}:
            continue
        season = _text(row.get("season"))
        element = _text(row.get("fpl_element"))
        code = _text(row.get("fpl_player_code"))
        if season and element:
            by_element.setdefault((season, element), []).append(row)
        if season and code:
            by_code.setdefault((season, code), []).append(row)
    return (
        {key: tuple(value) for key, value in by_element.items()},
        {key: tuple(value) for key, value in by_code.items()},
    )


@lru_cache(maxsize=1)
def _historical_index() -> dict[tuple[str, str], tuple[dict[str, str], ...]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in _historical_rows():
        if _text(row.get("identity_status")).upper() != "VERIFIED":
            continue
        season = _text(row.get("season"))
        element = _text(row.get("fpl_element"))
        if season and element:
            grouped.setdefault((season, element), []).append(row)
    return {key: tuple(value) for key, value in grouped.items()}


@lru_cache(maxsize=20)
def _rich_source_by_code(season: str) -> dict[str, str]:
    candidates: dict[str, set[str]] = {}
    for row in rich_player_projection._packaged_rows():
        if _text(row.get("season")) != season:
            continue
        code = _text(row.get("player_code"))
        source_id = _text(row.get("source_player_id"))
        if code and source_id:
            candidates.setdefault(code, set()).add(source_id)
    return {
        code: next(iter(source_ids))
        for code, source_ids in candidates.items()
        if len(source_ids) == 1
    }


def _record_ids(player: dict) -> tuple[set[str], set[str]]:
    elements: set[str] = set()
    explicit_codes: set[str] = set()
    for row in player.get("_records", ()):
        element = _text(row.get("element") or row.get("id"))
        code = _text(row.get("player_code"))
        if element:
            elements.add(element)
        if code:
            explicit_codes.add(code)
    return elements, explicit_codes


def _current_candidates(season: str, player: dict) -> list[dict[str, str]]:
    by_element, by_code = _current_indexes()
    elements, explicit_codes = _record_ids(player)
    route_code = _text(player.get("player_code"))
    output: dict[tuple[str, str], dict[str, str]] = {}
    for element in elements:
        for row in by_element.get((season, element), ()):
            output[(_text(row.get("player_identity_key")), _text(row.get("fpl_element")))] = row
    for code in {*explicit_codes, route_code}:
        if not code:
            continue
        for row in by_code.get((season, code), ()):
            output[(_text(row.get("player_identity_key")), _text(row.get("fpl_element")))] = row
    return list(output.values())


def _historical_candidates(season: str, player: dict) -> list[dict[str, str]]:
    elements, _explicit_codes = _record_ids(player)
    route_code = _text(player.get("player_code"))
    output: dict[str, dict[str, str]] = {}
    for element in {*elements, route_code}:
        if not element:
            continue
        for row in _historical_index().get((season, element), ()):
            source_id = _text(row.get("source_player_id"))
            if source_id:
                output[source_id] = row
    return list(output.values())


def _rich_direct_candidate(season: str, player: dict) -> tuple[str, str] | None:
    """Use an already-materialised exact PulseLive -> Player-Match edge.

    This fallback is allowed only when the FPL record exposes one explicit
    ``player_code``. A historical FPL element is never numerically compared
    with a PulseLive id.
    """
    _elements, explicit_codes = _record_ids(player)
    if len(explicit_codes) != 1:
        return None
    code = next(iter(explicit_codes))
    source_id = _rich_source_by_code(season).get(code)
    if not source_id:
        return None
    return source_id, code


def _portrait_code(season: str, player_match_source_id: str, hinted: str = "") -> str | None:
    hinted = _text(hinted)
    if hinted:
        return hinted
    return (
        rich_player_projection
        .pulselive_code_by_player_match_source_id(season)
        .get(player_match_source_id)
    )


def resolve_player_identity(season: str, player: dict) -> dict:
    route_code = _text(player.get("player_code"))

    current = _current_candidates(season, player)
    current_keys = {
        _text(row.get("player_identity_key"))
        for row in current
        if _text(row.get("player_identity_key"))
    }
    if len(current_keys) == 1:
        key = next(iter(current_keys))
        source_ids = {
            _text(row.get("player_match_source_player_id"))
            for row in current
            if _text(row.get("player_match_source_player_id"))
        }
        if len(source_ids) == 1:
            source_id = next(iter(source_ids))
            codes = {
                _text(row.get("fpl_player_code"))
                for row in current
                if _text(row.get("fpl_player_code"))
            }
            hinted = next(iter(codes)) if len(codes) == 1 else ""
            return {
                "available": True,
                "identity_status": "VERIFIED",
                "player_identity_key": key,
                "player_match_source_player_id": source_id,
                "seasonal_route_code": route_code,
                "portrait_player_code": _portrait_code(season, source_id, hinted),
                "identity_route": "TRACKED_FPL_PLAYER_IDENTITY_RELATIONSHIP",
                "limitations": [],
            }

    historical = _historical_candidates(season, player)
    historical_ids = {
        _text(row.get("source_player_id"))
        for row in historical
        if _text(row.get("source_player_id"))
    }
    if len(historical_ids) == 1:
        source_id = next(iter(historical_ids))
        return {
            "available": True,
            "identity_status": "VERIFIED",
            "player_identity_key": f"player_match:{source_id}",
            "player_match_source_player_id": source_id,
            "seasonal_route_code": route_code,
            "portrait_player_code": _portrait_code(season, source_id),
            "identity_route": "VERIFIED_HISTORICAL_FPL_ELEMENT_TO_PLAYER_MATCH",
            "limitations": [],
        }

    direct = _rich_direct_candidate(season, player)
    if direct is not None:
        source_id, portrait_code = direct
        return {
            "available": True,
            "identity_status": "SOURCE_NATIVE_VERIFIED",
            "player_identity_key": f"player_match:{source_id}",
            "player_match_source_player_id": source_id,
            "seasonal_route_code": route_code,
            "portrait_player_code": portrait_code,
            "identity_route": "MATERIALISED_PULSELIVE_TO_PLAYER_MATCH_EDGE",
            "limitations": [
                "Identity is source-native verified; no stronger canonical player identity is asserted."
            ],
        }

    return {
        "available": False,
        "identity_status": "UNRESOLVED",
        "player_identity_key": None,
        "player_match_source_player_id": None,
        "seasonal_route_code": route_code,
        "portrait_player_code": None,
        "identity_route": "UNRESOLVED",
        "limitations": [
            "No tracked verified relationship connects this seasonal Player Profile route to a reusable player identity."
        ],
    }


@lru_cache(maxsize=512)
def resolve_route_identity(season: str, player_code: str) -> dict:
    player = player_research.player_detail(season, player_code)
    if player is None:
        return {
            "available": False,
            "identity_status": "UNAVAILABLE",
            "player_identity_key": None,
            "player_match_source_player_id": None,
            "seasonal_route_code": _text(player_code),
            "portrait_player_code": None,
            "identity_route": "PLAYER_UNAVAILABLE",
            "limitations": ["Player Profile route is unavailable."],
        }
    return resolve_player_identity(season, player)


def _option(player: dict, season: str, identity: dict) -> dict:
    return {
        "season": season,
        "player_code": _text(player.get("player_code")),
        "player_name": _text(player.get("player_name")),
        "position": _text(player.get("position")),
        "clubs": list(player.get("clubs") or ()),
        "identity_status": _text(identity.get("identity_status")),
    }


@lru_cache(maxsize=512)
def profile_seasons(season: str, player_code: str) -> tuple[dict, ...]:
    seed = player_research.player_detail(season, player_code)
    if seed is None:
        return tuple()
    seed_identity = resolve_player_identity(season, seed)
    key = seed_identity.get("player_identity_key")
    if not key:
        return (_option(seed, season, seed_identity),)

    options: list[dict] = []
    for candidate_season in player_research.available_seasons():
        matches: list[tuple[dict, dict]] = []
        for candidate in player_research.season_players(candidate_season):
            identity = resolve_player_identity(candidate_season, candidate)
            if identity.get("player_identity_key") == key:
                matches.append((candidate, identity))
        if len(matches) == 1:
            candidate, identity = matches[0]
            options.append(_option(candidate, candidate_season, identity))

    options.sort(key=lambda row: int(row["season"][:4]), reverse=True)
    return tuple(options)


def clear_caches() -> None:
    _current_rows.cache_clear()
    _historical_rows.cache_clear()
    _current_indexes.cache_clear()
    _historical_index.cache_clear()
    _rich_source_by_code.cache_clear()
    resolve_route_identity.cache_clear()
    profile_seasons.cache_clear()


__all__ = [
    "CURRENT_RELATIONSHIPS",
    "HISTORICAL_REGISTRY",
    "clear_caches",
    "profile_seasons",
    "resolve_player_identity",
    "resolve_route_identity",
]
