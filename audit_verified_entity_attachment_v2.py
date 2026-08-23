from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ELIG = DATA / "variable_attachment_eligibility.csv"
OUT = DATA / "verified_entity_attachment_v2.csv"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        return list(r), r.fieldnames or []


def n(v):
    return str(v or "").strip()


def explicit_contract(row: dict[str, str], entity: str) -> bool:
    grain = n(row.get("grain")).lower()
    contract = n(row.get("identity_contract")).lower()
    if entity == "PLAYER":
        return grain in {"player", "player_match", "player_season"} or contract in {
            "fpl_player_to_frl_player_identity",
            "source_player_identity_to_player_season",
            "player_identity_to_player_match_observations",
        }
    if entity == "FIXTURE":
        return grain in {"fixture", "player_match", "team_match"} or contract == "canonical_fixture_to_source_match"
    if entity == "TEAM":
        return grain in {"team", "team_match", "squad"} or contract == "canonical_team_season_to_source_team"
    return False


def compatible(row: dict[str, str], entity: str) -> bool:
    grain = n(row.get("grain")).lower()
    if entity == "PLAYER":
        return grain in {"player", "player_season", "player_match"}
    if entity == "FIXTURE":
        return grain in {"fixture", "player_match", "team_match"}
    if entity == "TEAM":
        return grain in {"team", "team_match", "squad"}
    return False


def main():
    rows, cols = read_csv(ELIG)
    print("FRL VERIFIED ENTITY ATTACHMENT AUDIT V2")
    print("=" * 100)
    print(f"Eligibility rows: {len(rows)}")

    # Eligibility file is 3 rows per variable; consume its explicit classification.
    entities = {"PLAYER", "FIXTURE", "TEAM"}
    out = []
    counters = {e: Counter() for e in entities}

    for row in rows:
        entity = n(row.get("entity")).upper()
        if entity not in entities:
            # Support the first implementation if entity column is absent.
            entity = n(row.get("target_entity")).upper()
        if entity not in entities:
            continue

        status = n(row.get("eligibility_status"))
        if not status:
            # Use the status columns from the actual eligibility output.
            status = n(row.get(f"{entity.lower()}_eligibility"))

        is_compatible = status in {
            "GRAIN_COMPATIBLE",
            "GRAIN_OR_CONTRACT_COMPATIBLE",
        } or compatible(row, entity)

        contract = explicit_contract(row, entity)
        source_required = n(row.get("source_identity_required")).upper() == "TRUE"
        identity = n(row.get("identity_contract"))
        relationship = n(row.get("relationship_kind"))

        if not is_compatible:
            result = "NOT_STRUCTURALLY_ELIGIBLE"
        elif contract and (identity or relationship in {"ENTITY", "OBSERVATION"}):
            if source_required and not identity:
                result = "CONTRACT_SHAPE_PRESENT_SOURCE_IDENTITY_ROUTE_UNSPECIFIED"
            else:
                result = "EXPLICIT_CONTRACT_ROUTE_PRESENT_REQUIRES_EVIDENCE_CHECK"
        elif contract:
            result = "CONTRACT_PRESENT_REQUIRES_EVIDENCE_CHECK"
        else:
            result = "STRUCTURALLY_ELIGIBLE_NO_EXPLICIT_CONTRACT"

        counters[entity][result] += 1
        item = dict(row)
        item["verification_result"] = result
        item["explicit_contract_detected"] = "TRUE" if contract else "FALSE"
        item["source_identity_required_flag"] = "TRUE" if source_required else "FALSE"
        out.append(item)

    for entity in ("PLAYER", "FIXTURE", "TEAM"):
        print(f"\n{entity}")
        for k, v in counters[entity].most_common():
            print(f"  {v:5}  {k}")

    fields = list(dict.fromkeys((cols or []) + [
        "verification_result",
        "explicit_contract_detected",
        "source_identity_required_flag",
    ]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    print(f"\nOutput: {OUT}")
    print("Evidence-only verification; no inferred joins and no canonical promotion.")


if __name__ == "__main__":
    main()
