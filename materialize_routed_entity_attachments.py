"""Materialise normalized source-observation -> entity attachments for routed fields.

This deliberately avoids a field x observation Cartesian product. Variables inherit
attachments from their source family observation rows. Identity remains fail-closed.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from player_identity_registry import build_registry
from source_family_adapters import (
    season_fixtures,
    team_match_source_rows,
    player_match_source_rows,
    player_season_source_rows,
)
from squad_source_adapter import load_squad_payload, resolve_team_season, squad_player_rows
from pulselive_season_namespace import load_mapping

ROOT = Path(__file__).resolve().parent
ROUTED = ROOT / "data" / "routed_variable_attachment_registry_v2.csv"
OUT_DIR = ROOT / "data" / "entity_attachments"
TEAM_SEASONS = ROOT / "identity" / "team_seasons.csv"


def _n(value: object) -> str:
    return str(value or "").strip()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _team_registry() -> list[dict[str, str]]:
    return _read_csv(TEAM_SEASONS)


def _verified_player_map() -> dict[tuple[str, str], list[dict[str, str]]]:
    out: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in build_registry():
        key = (_n(row.get("season")), _n(row.get("source_player_id")))
        if key[0] and key[1] and _n(row.get("identity_status")) == "VERIFIED":
            out[key].append(row)
    return out


def _team_season_id(season: str, local_team_id: str, registry: list[dict[str, str]]) -> tuple[str, str]:
    matches = [
        row
        for row in registry
        if _n(row.get("season")) == season
        and _n(row.get("local_team_id")) == local_team_id
        and _n(row.get("mapping_status")) in ("", "VERIFIED")
    ]
    if len(matches) != 1:
        return "", "AMBIGUOUS_OR_MISSING"
    return _n(matches[0].get("team_season_id")), "VERIFIED"


def materialize_team_match(registry: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seasons = sorted({_n(r.get("season")) for r in _read_csv(ROOT / "fixtures_master_corrected.csv") if _n(r.get("season"))})
    print(f"  team_match: {len(seasons)} seasons", flush=True)
    for index, season in enumerate(seasons, start=1):
        fixtures = season_fixtures(season)
        for fixture in fixtures:
            fixture_id = _n(fixture.get("fixture_id"))
            try:
                home, away = team_match_source_rows(season, fixture_id)
            except ValueError:
                continue
            for venue, source_row in (("HOME", home), ("AWAY", away)):
                local_team_id = _n(fixture.get("home_team_id" if venue == "HOME" else "away_team_id"))
                team_season_id, team_status = _team_season_id(season, local_team_id, registry)
                rows.append({
                    "grain": "team_match",
                    "season": season,
                    "fixture_id": fixture_id,
                    "source_match_id": _n(source_row.get("matchId") or source_row.get("match_id")),
                    "venue_role": venue,
                    "source_team_id": local_team_id,
                    "team_season_id": team_season_id,
                    "fixture_attachment_status": "VERIFIED_SOURCE_MATCH_ROUTE",
                    "team_attachment_status": team_status,
                })
        print(f"    [{index:02d}/{len(seasons):02d}] {season}: {len(fixtures)} fixtures", flush=True)
    return rows


def materialize_player_match(registry: list[dict[str, str]], player_map: dict[tuple[str, str], list[dict[str, str]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seasons = sorted({_n(r.get("season")) for r in _read_csv(ROOT / "fixtures_master_corrected.csv") if _n(r.get("season"))})
    print(f"  player_match: {len(seasons)} seasons", flush=True)
    for index, season in enumerate(seasons, start=1):
        fixtures = season_fixtures(season)
        for fixture in fixtures:
            fixture_id = _n(fixture.get("fixture_id"))
            try:
                source_rows = player_match_source_rows(season, fixture_id)
            except ValueError:
                continue
            for source_row in source_rows:
                source_player_id = _n(source_row.get("playerId") or source_row.get("player_id") or source_row.get("pl_code"))
                candidates = player_map.get((season, source_player_id), [])
                player_status = "VERIFIED" if len(candidates) == 1 else ("AMBIGUOUS" if len(candidates) > 1 else "UNRESOLVED")
                team_id = _n(source_row.get("team_id") or source_row.get("teamId"))
                team_season_id, team_status = _team_season_id(season, team_id, registry) if team_id else ("", "UNAVAILABLE")
                rows.append({
                    "grain": "player_match",
                    "season": season,
                    "fixture_id": fixture_id,
                    "source_player_id": source_player_id,
                    "fixture_attachment_status": "VERIFIED_SOURCE_MATCH_ROUTE",
                    "player_attachment_status": player_status,
                    "team_attachment_status": team_status if team_id else "NOT_DIRECTLY_EXPOSED",
                    "team_season_id": team_season_id,
                    "frl_player_identity_status": _n(candidates[0].get("identity_status")) if len(candidates) == 1 else "",
                })
        print(f"    [{index:02d}/{len(seasons):02d}] {season}: {len(fixtures)} fixtures", flush=True)
    return rows


def materialize_player_season(player_map: dict[tuple[str, str], list[dict[str, str]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seasons = sorted({_n(r.get("season")) for r in _read_csv(ROOT / "player_identity_registry.csv") if _n(r.get("season"))})
    print(f"  player_season: {len(seasons)} seasons", flush=True)
    for index, season in enumerate(seasons, start=1):
        source_rows = player_season_source_rows(season)
        for source_row in source_rows:
            source_player_id = _n(source_row.get("playerId"))
            candidates = player_map.get((season, source_player_id), [])
            status = "VERIFIED" if len(candidates) == 1 else ("AMBIGUOUS" if len(candidates) > 1 else "UNRESOLVED")
            rows.append({
                "grain": "player_season",
                "season": season,
                "source_player_id": source_player_id,
                "player_attachment_status": status,
                "frl_player_identity_status": _n(candidates[0].get("identity_status")) if len(candidates) == 1 else "",
                "player_season_source_name": _n(source_row.get("playerName")),
            })
        print(f"    [{index:02d}/{len(seasons):02d}] {season}: {len(source_rows)} player-season rows", flush=True)
    return rows


def materialize_squad(registry: list[dict[str, str]]) -> list[dict[str, object]]:
    print("  squad: loading live squad payload", flush=True)
    payload = load_squad_payload()
    context = resolve_team_season(payload, source_season_map=load_mapping(), registry=registry)
    rows: list[dict[str, object]] = []
    if context.get("status") == "VERIFIED_TEAM_SEASON_ROUTE":
        players = squad_player_rows(payload)
        for player in players:
            rows.append({
                "grain": "squad",
                "season": _n(context.get("season")),
                "source_season_id": _n(context.get("source_season_id")),
                "source_team_id": _n(context.get("source_team_id")),
                "team_season_id": _n(context.get("team_season_id")),
                "source_player_id": _n(player.get("id")),
                "team_attachment_status": "VERIFIED",
                "player_attachment_status": "SOURCE_NATIVE_ONLY",
            })
        print(f"    squad route: VERIFIED_TEAM_SEASON_ROUTE; {len(players)} players", flush=True)
    else:
        rows.append({
            "grain": "squad",
            "season": _n(context.get("season")),
            "source_season_id": _n(context.get("source_season_id")),
            "source_team_id": _n(context.get("source_team_id")),
            "team_season_id": "",
            "source_player_id": "",
            "team_attachment_status": _n(context.get("status")),
            "player_attachment_status": "SOURCE_NATIVE_ONLY",
        })
        print(f"    squad route: {_n(context.get('status'))}", flush=True)
    return rows


def main() -> None:
    routed = _read_csv(ROUTED)
    registry = _team_registry()
    player_map = _verified_player_map()

    variable_rows = [
        {
            "field_name": _n(row.get("field_name")),
            "grain": _n(row.get("grain")),
            "resource": _n(row.get("resource")),
            "identity_contract": _n(row.get("identity_contract")),
        }
        for row in routed
    ]

    print("FRL ROUTED ENTITY ATTACHMENT MATERIALISATION", flush=True)
    print("=" * 80, flush=True)
    print(f"Routed variables: {len(variable_rows)}", flush=True)
    print("[1/4] TEAM-MATCH", flush=True)
    team_match = materialize_team_match(registry)
    print("[2/4] PLAYER-MATCH", flush=True)
    player_match = materialize_player_match(registry, player_map)
    print("[3/4] PLAYER-SEASON", flush=True)
    player_season = materialize_player_season(player_map)
    print("[4/4] SQUAD", flush=True)
    squad = materialize_squad(registry)

    _write_csv(OUT_DIR / "routed_variable_family_map.csv", variable_rows)
    _write_csv(OUT_DIR / "team_match_observation_attachments.csv", team_match)
    _write_csv(OUT_DIR / "player_match_observation_attachments.csv", player_match)
    _write_csv(OUT_DIR / "player_season_observation_attachments.csv", player_season)
    _write_csv(OUT_DIR / "squad_observation_attachments.csv", squad)

    print()
    print("MATERIALISATION SUMMARY")
    print(f"team_match observations: {len(team_match)}")
    print(f"player_match observations: {len(player_match)}")
    print(f"player_season observations: {len(player_season)}")
    print(f"squad observations: {len(squad)}")
    for name, rows, key in (
        ("PLAYER_MATCH PLAYER", player_match, "player_attachment_status"),
        ("PLAYER_SEASON PLAYER", player_season, "player_attachment_status"),
        ("TEAM_MATCH TEAM", team_match, "team_attachment_status"),
        ("SQUAD TEAM", squad, "team_attachment_status"),
    ):
        counts = Counter(_n(r.get(key)) for r in rows)
        print(name)
        for status, count in counts.most_common():
            print(f"  {count:6d} {status or 'UNSPECIFIED'}")
    print()
    print(f"Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
