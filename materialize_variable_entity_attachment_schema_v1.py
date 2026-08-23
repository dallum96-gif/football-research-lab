"""Materialise the frozen V1 variable/entity attachment schema.

This is an additive seam over the existing routed observation materialiser.
It does not replace source adapters, identity registries, or canonical data.
No identity inference is performed.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import materialize_routed_entity_attachments as routed

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "entity_attachments_v1"


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


def _player_match(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for i, row in enumerate(rows, start=1):
        out.append({
            "observation_id": _n(row.get("observation_id")) or f"player_match/{i}",
            "grain": "player_match",
            "season": _n(row.get("season")),
            "source_record_id": _n(row.get("source_match_id")),
            "source_player_id": _n(row.get("source_player_id")),
            "source_match_id": _n(row.get("source_match_id")),
            "source_team_id": _n(row.get("source_team_id")),
            "fixture_attachment_status": _status(row.get("fixture_attachment_status")),
            "fixture_entity_id": _n(row.get("fixture_id")),
            "home_team_attachment_status": _status(row.get("home_team_attachment_status")),
            "home_team_entity_id": _n(row.get("home_team_attachment_entity_id")),
            "away_team_attachment_status": _status(row.get("away_team_attachment_status")),
            "away_team_entity_id": _n(row.get("away_team_attachment_entity_id")),
            "player_attachment_status": _status(row.get("player_attachment_status")),
            "player_entity_id": _n(row.get("player_attachment_entity_id")),
            "participation_status": _n(row.get("participation_status")),
            "attachment_basis_fixture": "legacy routed materialiser: verified source-match route",
            "attachment_basis_team": "legacy routed materialiser: verified team-season route",
            "attachment_basis_player": _n(row.get("attachment_basis_player")) or "verified player identity registry only",
        })
    return out


def _player_season(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for i, row in enumerate(rows, start=1):
        out.append({
            "observation_id": _n(row.get("observation_id")) or f"player_season/{i}",
            "grain": "player_season",
            "season": _n(row.get("season")),
            "source_record_id": _n(row.get("observation_id")),
            "source_player_id": _n(row.get("source_player_id")),
            "source_match_id": "",
            "source_team_id": _n(row.get("team_season_id")),
            "fixture_attachment_status": "NOT_APPLICABLE",
            "fixture_entity_id": "",
            "home_team_attachment_status": "NOT_APPLICABLE",
            "home_team_entity_id": "",
            "away_team_attachment_status": "NOT_APPLICABLE",
            "away_team_entity_id": "",
            "player_attachment_status": _status(row.get("player_attachment_status")),
            "player_entity_id": _n(row.get("player_attachment_entity_id")),
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


def _squad(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for i, row in enumerate(rows, start=1):
        out.append({
            "observation_id": _n(row.get("observation_id")) or f"squad/{i}",
            "grain": "squad",
            "season": _n(row.get("season")),
            "source_record_id": _n(row.get("observation_id")),
            "source_player_id": _n(row.get("source_player_id")),
            "source_match_id": "",
            "source_team_id": _n(row.get("source_team_id")),
            "fixture_attachment_status": "NOT_APPLICABLE",
            "fixture_entity_id": "",
            "home_team_attachment_status": "NOT_APPLICABLE",
            "home_team_entity_id": "",
            "away_team_attachment_status": "NOT_APPLICABLE",
            "away_team_entity_id": "",
            "player_attachment_status": _status(row.get("player_attachment_status")),
            "player_entity_id": _n(row.get("player_attachment_entity_id")),
            "team_attachment_status": _status(row.get("team_attachment_status")),
            "team_season_id": _n(row.get("team_season_attachment_entity_id")),
        })
    return out


def main() -> None:
    routed_rows = routed._read_csv(routed.ROUTED)
    registry = routed._team_registry()
    player_map = routed._verified_player_map()

    print("FRL VARIABLE -> ENTITY ATTACHMENT SCHEMA V1 MATERIALISATION")
    print("=" * 96)
    variables = _variable_map(routed_rows)
    print(f"Variables: {len(variables):,}")

    team_match = _team_match(routed.materialize_team_match(registry))
    player_match = _player_match(routed.materialize_player_match(registry, player_map))
    player_season = _player_season(routed.materialize_player_season(registry, player_map))
    squad = _squad(routed.materialize_squad(registry))

    _write(OUT / "variable.csv", variables)
    _write(OUT / "team_match_observation.csv", team_match)
    _write(OUT / "player_match_observation.csv", player_match)
    _write(OUT / "player_season_observation.csv", player_season)
    _write(OUT / "squad_observation.csv", squad)

    print()
    print("SCHEMA V1 OUTPUT")
    print(f"  variable:                    {len(variables):,}")
    print(f"  team_match observations:     {len(team_match):,}")
    print(f"  player_match observations:   {len(player_match):,}")
    print(f"  player_season observations:  {len(player_season):,}")
    print(f"  squad observations:          {len(squad):,}")
    print(f"Output: {OUT}")
    print("No canonical identity promotion is performed.")


if __name__ == "__main__":
    main()
