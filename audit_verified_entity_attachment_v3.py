from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ELIG = DATA / "variable_attachment_eligibility.csv"
OUT = DATA / "verified_entity_attachment_v3.csv"


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
        return grain in {"fixture", "player_match", "team_match", "event"} or contract == "canonical_fixture_to_source_match"
    if entity == "TEAM":
        return grain in {"team", "team_match", "squad"} or contract == "canonical_team_season_to_source_team"
    return False


def compatible(row: dict[str, str], entity: str) -> bool:
    grain = n(row.get("grain")).lower()
    if entity == "PLAYER":
        return grain in {"player", "player_season", "player_match"}
    if entity == "FIXTURE":
        return grain in {"fixture", "player_match", "team_match", "event"} or n(row.get("identity_contract")) == "canonical_fixture_to_source_match"
    if entity == "TEAM":
        return grain in {"team", "team_match", "squad"} or n(row.get("identity_contract")) == "canonical_team_season_to_source_team"
    return False


def entity_status(row: dict[str, str], entity: str) -> str:
    # Current one-row-per-variable format.
    current = n(row.get(f"eligibility_{entity.lower()}"))
    if current:
        return current

    # Older three-row-per-variable formats.
    direct = n(row.get("eligibility_status"))
    if direct:
        return direct

    return ""


def main() -> None:
    if not ELIG.is_file():
        raise SystemExit(f"Missing eligibility file: {ELIG}")

    rows, cols = read_csv(ELIG)
    print("FRL VERIFIED ENTITY ATTACHMENT AUDIT V3")
    print("=" * 100)
    print(f"Eligibility rows: {len(rows)}")
    print("Accepts both current one-row and legacy three-row eligibility formats.")

    entities = ("PLAYER", "FIXTURE", "TEAM")
    counters = {e: Counter() for e in entities}
    out = []
    seen = Counter()

    for row in rows:
        for entity in entities:
            status = entity_status(row, entity)
            if not status:
                # In a legacy entity-row format, only evaluate the current entity.
                row_entity = n(row.get("entity") or row.get("target_entity")).upper()
                if row_entity != entity:
                    continue
                status = n(row.get("eligibility_status"))

            if not status:
                continue

            is_compatible = status in {"GRAIN_COMPATIBLE", "GRAIN_OR_CONTRACT_COMPATIBLE"} or compatible(row, entity)
            contract = explicit_contract(row, entity)
            source_required = n(row.get("source_identity_required")).upper() == "TRUE"
            identity_contract = n(row.get("identity_contract"))
            relationship = n(row.get("relationship_kind"))

            if not is_compatible:
                result = "NOT_STRUCTURALLY_ELIGIBLE"
            elif contract and (identity_contract or relationship in {"ENTITY", "OBSERVATION"}):
                if source_required and not identity_contract:
                    result = "CONTRACT_SHAPE_PRESENT_SOURCE_IDENTITY_ROUTE_UNSPECIFIED"
                else:
                    result = "EXPLICIT_CONTRACT_ROUTE_PRESENT_REQUIRES_EVIDENCE_CHECK"
            elif contract:
                result = "CONTRACT_PRESENT_REQUIRES_EVIDENCE_CHECK"
            else:
                result = "STRUCTURALLY_ELIGIBLE_NO_EXPLICIT_CONTRACT"

            counters[entity][result] += 1
            item = dict(row)
            item["target_entity"] = entity
            item["eligibility_status_used"] = status
            item["verification_result"] = result
            item["explicit_contract_detected"] = "TRUE" if contract else "FALSE"
            item["source_identity_required_flag"] = "TRUE" if source_required else "FALSE"
            out.append(item)
            seen[(n(row.get("field_name")), entity)] += 1

    print("\nROWS EVALUATED")
    for entity in entities:
        print(f"  {entity:<8} {sum(counters[entity].values()):5}")

    for entity in entities:
        print(f"\n{entity}")
        for k, v in counters[entity].most_common():
            print(f"  {v:5}  {k}")

    fields = list(dict.fromkeys((cols or []) + [
        "target_entity",
        "eligibility_status_used",
        "verification_result",
        "explicit_contract_detected",
        "source_identity_required_flag",
    ]))
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out)

    print(f"\nOutput: {OUT}")
    print("Evidence-only verification; no inferred joins and no canonical promotion.")


if __name__ == "__main__":
    main()
