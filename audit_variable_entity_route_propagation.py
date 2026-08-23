"""Audit propagation of established FRL entity routes to compatible variables.

Read-only. This does not create joins or promote identities. It distinguishes:
- verified route family available in existing FRL evidence;
- explicit contract present but route evidence still needs observation-level checks;
- grain-compatible without an explicit contract;
- structurally inapplicable.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MATRIX = DATA / "variable_entity_attachment_matrix.csv"
INHERITANCE = DATA / "team_match_variable_inheritance_audit.csv"
OUT = DATA / "variable_entity_route_propagation.csv"


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.is_file():
        return [], []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader), reader.fieldnames or []


def n(value: object) -> str:
    return str(value or "").strip()


def contract_for(row: dict[str, str], entity: str) -> bool:
    grain = n(row.get("grain")).lower()
    contract = n(row.get("identity_contract")).lower()
    if entity == "PLAYER":
        return grain in {"player", "player_season", "player_match"} or contract in {
            "fpl_player_to_frl_player_identity",
            "source_player_identity_to_player_season",
            "player_identity_to_player_match_observations",
        }
    if entity == "FIXTURE":
        return grain in {"fixture", "player_match", "team_match", "event"} or contract == "canonical_fixture_to_source_match"
    if entity == "TEAM":
        return grain in {"team", "team_match", "squad"} or contract == "canonical_team_season_to_source_team"
    return False


def compatible(row: dict[str, str], entity: str) -> bool:
    grain = n(row.get("grain")).lower()
    if entity == "PLAYER":
        return grain in {"player", "player_season", "player_match"}
    if entity == "FIXTURE":
        return grain in {"fixture", "player_match", "team_match", "event"}
    if entity == "TEAM":
        return grain in {"team", "team_match", "squad"}
    return False


def route_family(row: dict[str, str], entity: str) -> str:
    grain = n(row.get("grain")).lower()
    contract = n(row.get("identity_contract")).lower()
    resource = n(row.get("resource")).lower()

    if entity == "FIXTURE":
        if contract == "canonical_fixture_to_source_match" or grain == "fixture":
            return "CANONICAL_FIXTURE_TO_SOURCE_MATCH"
        if grain in {"team_match", "player_match", "event"} or resource == "match":
            return "FIXTURE_CONTEXT_INHERITANCE"
    elif entity == "TEAM":
        if contract == "canonical_team_season_to_source_team" or grain == "team":
            return "CANONICAL_TEAM_SEASON_TO_SOURCE_TEAM"
        if grain in {"team_match", "squad"}:
            return "TEAM_SEASON_INHERITANCE"
    elif entity == "PLAYER":
        if contract == "fpl_player_to_frl_player_identity":
            return "FPL_TO_FRL_PLAYER_IDENTITY"
        if contract == "source_player_identity_to_player_season" or grain == "player_season":
            return "SOURCE_PLAYER_TO_PLAYER_SEASON"
        if contract == "player_identity_to_player_match_observations" or grain == "player_match":
            return "PLAYER_IDENTITY_TO_PLAYER_MATCH"
        if grain == "player":
            return "PLAYER_IDENTITY"
    return "NONE"


def route_evidence_status(row: dict[str, str], entity: str, inheritance_names: set[str]) -> str:
    field = n(row.get("field_name"))
    grain = n(row.get("grain")).lower()
    contract = n(row.get("identity_contract")).lower()

    if entity == "TEAM" and grain == "team_match" and field in inheritance_names:
        return "VERIFIED_TEAM_MATCH_INHERITANCE"

    if entity == "FIXTURE" and contract == "canonical_fixture_to_source_match":
        return "EXPLICIT_FIXTURE_CONTRACT_REQUIRES_ROW_CHECK"

    if entity == "TEAM" and contract == "canonical_team_season_to_source_team":
        return "EXPLICIT_TEAM_CONTRACT_REQUIRES_ROW_CHECK"

    if entity == "PLAYER" and contract == "fpl_player_to_frl_player_identity":
        return "PLAYER_IDENTITY_REGISTRY_ROUTE"
    if entity == "PLAYER" and contract == "source_player_identity_to_player_season":
        return "SOURCE_PLAYER_SEASON_ROUTE"
    if entity == "PLAYER" and contract == "player_identity_to_player_match_observations":
        return "PLAYER_MATCH_CONTRACT_REQUIRES_OBSERVATION_CHECK"

    if compatible(row, entity):
        return "GRAIN_COMPATIBLE_NO_EXPLICIT_CONTRACT"
    return "NOT_APPLICABLE"


def main() -> None:
    rows, matrix_cols = read_csv(MATRIX)
    inheritance_rows, _ = read_csv(INHERITANCE)
    inheritance_names = {
        n(r.get("field_name"))
        for r in inheritance_rows
        if n(r.get("inheritance_status")).upper() == "INHERITS_TEAM_MATCH_ROUTE"
        or n(r.get("status")).upper() == "INHERITS_TEAM_MATCH_ROUTE"
    }

    out: list[dict[str, str]] = []
    counters = {e: Counter() for e in ("PLAYER", "FIXTURE", "TEAM")}

    for row in rows:
        for entity in ("PLAYER", "FIXTURE", "TEAM"):
            ok = compatible(row, entity)
            contract = contract_for(row, entity)
            family = route_family(row, entity)
            evidence = route_evidence_status(row, entity, inheritance_names)
            if not ok:
                result = "NOT_STRUCTURALLY_APPLICABLE"
            elif evidence.startswith("VERIFIED_"):
                result = evidence
            elif contract:
                result = "CONTRACT_ROUTE_PRESENT_REQUIRES_EVIDENCE_CHECK"
            else:
                result = "GRAIN_COMPATIBLE_NO_CONTRACT"
            counters[entity][result] += 1
            item = dict(row)
            item.update({
                "target_entity": entity,
                "route_family": family,
                "route_evidence_status": evidence,
                "route_propagation_status": result,
            })
            out.append(item)

    print("FRL VARIABLE -> ENTITY ROUTE PROPAGATION AUDIT")
    print("=" * 100)
    print(f"Variables reviewed: {len(rows)}")
    print("Route propagation is evidence-only; no inferred joins and no canonical promotion.")
    for entity in ("PLAYER", "FIXTURE", "TEAM"):
        print(f"\n{entity}")
        for key, value in counters[entity].most_common():
            print(f"  {value:6}  {key}")

    fields = list(dict.fromkeys(matrix_cols + [
        "target_entity", "route_family", "route_evidence_status", "route_propagation_status"
    ]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)
    print(f"\nOutput: {OUT}")


if __name__ == "__main__":
    main()
