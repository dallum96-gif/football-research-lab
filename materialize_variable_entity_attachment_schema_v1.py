"""Materialise the frozen V1 variable/entity attachment schema.

This is an additive seam over the existing routed observation materialiser.
It does not replace source adapters, identity registries, or canonical data.
No identity inference is performed.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import materialize_routed_entity_attachments as routed
import player_research

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "entity_attachments_v1"
FIXTURES = ROOT / "fixtures_master_corrected.csv"


def _n(value: Any) -> str:
    return str(value or "").strip()


def _status(value: Any, *, default: str = "UNRESOLVED") -> str:
    raw = _n(value).upper()
    if raw == "VERIFIED" or raw.endswith("_VERIFIED") or raw.startswith("VERIFIED_"):
        return "VERIFIED"
    if raw in {"REVIEW", "AMBIGUOUS", "AMBIGUOUS_OR_MISSING"} or "AMBIG" in raw:
        return "REVIEW"
    if raw in {"NOT_APPLICABLE", "NOT_DIRECTLY_EXPOSED"}:
        return "NOT_APPLICABLE"
    if raw in {"UNRESOLVED", "SOURCE_NATIVE_ONLY", ""}:
        return default
    return default


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _variable_map(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "field_name": _n(row.get("field_name")),
            "source_family": _n(row.get("source_family")),
            "resource": _n(row.get("resource")),
            "grain": _n(row.get("grain")),
            "field_type": _n(row.get("field_type")),
            "semantic_status": _n(row.get("semantic_status")),
            "relationship_kind": _n(row.get("relationship_kind")),
            "source_identity_required": _n(row.get("source_identity_required")),
            "provenance_requirement": _n(row.get("provenance_requirement")),
            "identity_contract": _n(row.get("identity_contract")),
        }
        for row in rows
    ]


def _fixture_map() -> dict[tuple[str, str], dict[str, str]]:
    return {
        (_n(row.get("season")), _n(row.get("fixture_id"))): row
        for row in routed._read_csv(FIXTURES)
        if _n(row.get("season")) and _n(row.get("fixture_id"))
    }


def _research_identity_map() -> dict[tuple[str, str], set[str]]:
    """Map (season, seasonal player key) to existing Player Research identity."""
    index: dict[tuple[str, str], set[str]] = defaultdict(set)
    for season in player_research.available_seasons():
        for row in player_research._load_season_rows(season):
            player_key = player_research.seasonal_player_id(row).strip()
            canonical = player_research.canonical_player_name(row).strip()
            if player_key and canonical:
                index[(season, player_key)].add(canonical)
    return index


def _verified_registry_research_map(
    registry_rows: list[dict[str, str]],
) -> dict[str, set[str]]:
    """Map source player IDs to existing unique Research identities via the verified registry."""
    research_index = _research_identity_map()
    out: dict[str, set[str]] = defaultdict(set)
    for row in registry_rows:
        if _n(row.get("identity_status")) != "VERIFIED":
            continue
        season = _n(row.get("season"))
        player_key = _n(row.get("fpl_element"))
        source_id = _n(row.get("source_player_id"))
        if not season or not player_key or not source_id:
            continue
        for canonical in research_index.get((season, player_key), set()):
            out[source_id].add(canonical)
    return out


def _player_identity_attachment(
    season: str,
    source_player_id: str,
    direct_candidates: list[dict[str, str]],
    research_map: dict[str, set[str]],
) -> tuple[str, str, str, str]:
    """Return status, entity key, source ref and evidence basis."""
    if len(direct_candidates) == 1:
        canonical = research_map.get(source_player_id, set())
        if len(canonical) == 1:
            identity = next(iter(canonical))
            return (
                "VERIFIED",
                f"research:{identity}",
                source_player_id,
                "verified registry direct route + existing Player Research identity",
            )
        return (
            "VERIFIED",
            "",
            source_player_id,
            "verified source player identity; Player Research identity not uniquely closed",
        )
    if len(direct_candidates) > 1:
        return (
            "REVIEW",
            "",
            source_player_id,
            "verified registry contains multiple candidates for source player identity",
        )

    canonical = research_map.get(source_player_id, set())
    if len(canonical) == 1:
        identity = next(iter(canonical))
        return (
            "VERIFIED",
            f"research:{identity}",
            source_player_id,
            "verified registry closure via existing Player Research identity",
        )
    if len(canonical) > 1:
        return (
            "REVIEW",
            "",
            source_player_id,
            "verified registry closure reaches multiple Player Research identities",
        )
    return (
        "UNRESOLVED",
        "",
        source_player_id,
        "no existing verified Player Research closure",
    )


def _player_match(
    rows: list[dict[str, Any]],
    registry: list[dict[str, str]],
    fixtures: dict[tuple[str, str], dict[str, str]],
    research_map: dict[str, set[str]],
    player_map: dict[tuple[str, str], list[dict[str, str]]],
) -> list[dict[str, Any]]:
    out = []
    for i, row in enumerate(rows, start=1):
        season = _n(row.get("season"))
        fixture_id = _n(row.get("fixture_id"))
        fixture = fixtures.get((season, fixture_id), {})
        home_local_id = _n(fixture.get("home_team_id"))
        away_local_id = _n(fixture.get("away_team_id"))
        home_team_id, home_status = routed._team_season_id(season, home_local_id, registry)
        away_team_id, away_status = routed._team_season_id(season, away_local_id, registry)
        source_player_id = _n(row.get("source_player_id"))
        direct_candidates = player_map.get((season, source_player_id), [])
        player_status, player_entity_id, player_source_ref, player_basis = _player_identity_attachment(
            season,
            source_player_id,
            direct_candidates,
            research_map,
        )
        out.append({
            "observation_id": _n(row.get("observation_id")) or f"player_match/{i}",
            "grain": "player_match",
            "season": season,
            "source_record_id": _n(row.get("source_match_id")),
            "source_player_id": source_player_id,
            "source_match_id": _n(row.get("source_match_id")),
            "source_team_id": _n(row.get("source_team_id")),
            "fixture_attachment_status": _status(row.get("fixture_attachment_status")),
            "fixture_entity_id": fixture_id,
            "home_team_attachment_status": home_status,
            "home_team_entity_id": home_team_id,
            "away_team_attachment_status": away_status,
            "away_team_entity_id": away_team_id,
            "source_player_identity_status": "VERIFIED" if source_player_id else "UNRESOLVED",
            "player_attachment_status": player_status,
            "player_entity_id": player_entity_id,
            "player_source_identity_ref": player_source_ref,
            "participation_status": _n(row.get("participation_status")),
            "attachment_basis_fixture": "verified canonical_fixture_to_source_match route",
            "attachment_basis_team": "verified fixture home/away team relationship via identity/team_seasons.csv",
            "attachment_basis_player": player_basis,
        })
    return out


def _player_season(
    rows: list[dict[str, Any]],
    research_map: dict[str, set[str]],
) -> list[dict[str, Any]]:
    out = []
    for i, row in enumerate(rows, start=1):
        source_id = _n(row.get("source_player_id"))
        player_status, player_entity_id, player_source_ref, player_basis = _player_identity_attachment(
            _n(row.get("season")),
            source_id,
            [],
            research_map,
        )
        out.append({
            "observation_id": _n(row.get("observation_id")) or f"player_season/{i}",
            "grain": "player_season",
            "season": _n(row.get("season")),
            "source_record_id": _n(row.get("observation_id")),
            "source_player_id": source_id,
            "source_match_id": "",
            "source_team_id": "",
            "fixture_attachment_status": "NOT_APPLICABLE",
            "fixture_entity_id": "",
            "home_team_attachment_status": "NOT_APPLICABLE",
            "home_team_entity_id": "",
            "away_team_attachment_status": "NOT_APPLICABLE",
            "away_team_entity_id": "",
            "source_player_identity_status": "VERIFIED" if source_id else "UNRESOLVED",
            "player_attachment_status": player_status,
            "player_entity_id": player_entity_id,
            "player_source_identity_ref": player_source_ref,
            "team_attachment_status": _status(row.get("team_attachment_status")),
            "team_season_id": _n(row.get("team_season_id")),
            "attachment_basis_player": player_basis,
        })
    return out


def _team_match(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for i, row in enumerate(rows, start=1):
        out.append({
            "observation_id": f"team_match/{i}",
            "grain": "team_match",
            "season": _n(row.get("season")),
            "source_record_id": _n(row.get("source_match_id")),
            "source_player_id": "",
            "source_match_id": _n(row.get("source_match_id")),
            "source_team_id": _n(row.get("source_team_id")),
            "fixture_attachment_status": _status(row.get("fixture_attachment_status")),
            "fixture_entity_id": _n(row.get("fixture_id")),
            "home_team_attachment_status": _status(row.get("home_team_attachment_status"), default="NOT_APPLICABLE"),
            "home_team_entity_id": _n(row.get("home_team_attachment_entity_id")),
            "away_team_attachment_status": _status(row.get("away_team_attachment_status"), default="NOT_APPLICABLE"),
            "away_team_entity_id": _n(row.get("away_team_attachment_entity_id")),
            "player_attachment_status": "NOT_APPLICABLE",
            "player_entity_id": "",
            "team_attachment_status": _status(row.get("team_attachment_status")),
            "team_season_id": _n(row.get("team_season_id")),
        })
    return out


def _squad(rows: list[dict[str, Any]], research_map: dict[str, set[str]]) -> list[dict[str, Any]]:
    out = []
    for i, row in enumerate(rows, start=1):
        source_id = _n(row.get("source_player_id"))
        player_status, player_entity_id, player_source_ref, player_basis = _player_identity_attachment(
            _n(row.get("season")),
            source_id,
            [],
            research_map,
        )
        out.append({
            "observation_id": _n(row.get("observation_id")) or f"squad/{i}",
            "grain": "squad",
            "season": _n(row.get("season")),
            "source_record_id": _n(row.get("observation_id")),
            "source_player_id": source_id,
            "source_match_id": "",
            "source_team_id": _n(row.get("source_team_id")),
            "fixture_attachment_status": "NOT_APPLICABLE",
            "fixture_entity_id": "",
            "home_team_attachment_status": "NOT_APPLICABLE",
            "home_team_entity_id": "",
            "away_team_attachment_status": "NOT_APPLICABLE",
            "away_team_entity_id": "",
            "source_player_identity_status": "VERIFIED" if source_id else "UNRESOLVED",
            "player_attachment_status": player_status,
            "player_entity_id": player_entity_id,
            "player_source_identity_ref": player_source_ref,
            "team_attachment_status": _status(row.get("team_attachment_status")),
            "team_season_id": _n(row.get("team_season_attachment_entity_id")),
            "attachment_basis_player": player_basis,
        })
    return out


def main() -> None:
    routed_rows = routed._read_csv(routed.ROUTED)
    registry = routed._team_registry()
    player_map = routed._verified_player_map()
    research_map = _verified_registry_research_map(routed._read_csv(ROOT / "player_identity_registry.csv"))
    fixtures = _fixture_map()
    print("FRL VARIABLE -> ENTITY ATTACHMENT SCHEMA V1 MATERIALISATION")
    print("=" * 96)
    variables = _variable_map(routed_rows)
    print(f"Variables: {len(variables):,}")
    team_match = _team_match(routed.materialize_team_match(registry))
    player_match_rows = routed.materialize_player_match(registry, player_map)
    player_match = _player_match(player_match_rows, registry, fixtures, research_map, player_map)
    player_season = _player_season(routed.materialize_player_season(player_map), research_map)
    squad = _squad(routed.materialize_squad(registry), research_map)
    _write(OUT / "variable.csv", variables)
    _write(OUT / "team_match_observation.csv", team_match)
    _write(OUT / "player_match_observation.csv", player_match)
    _write(OUT / "player_season_observation.csv", player_season)
    _write(OUT / "squad_observation.csv", squad)
    _write(
        OUT / "player_research_identity_closure.csv",
        [
            {
                "source_player_id": source_id,
                "canonical_player_identity": next(iter(identities)) if len(identities) == 1 else "",
                "closure_status": "VERIFIED" if len(identities) == 1 else ("REVIEW" if len(identities) > 1 else "UNRESOLVED"),
                "evidence_basis": "verified player_identity_registry.csv + existing Player Research identity semantics",
            }
            for source_id, identities in sorted(research_map.items())
        ],
    )
    print()
    print("SCHEMA V1 OUTPUT")
    print(f"  variable:                    {len(variables):,}")
    print(f"  team_match observations:     {len(team_match):,}")
    print(f"  player_match observations:   {len(player_match):,}")
    print(f"  player_season observations:  {len(player_season):,}")
    print(f"  squad observations:          {len(squad):,}")
    print(f"  player research identities:  {sum(1 for identities in research_map.values() if len(identities) == 1):,} unique / {len(research_map):,} anchored")
    print(f"Output: {OUT}")
    print("No canonical identity promotion is performed.")


if __name__ == "__main__":
    main()
