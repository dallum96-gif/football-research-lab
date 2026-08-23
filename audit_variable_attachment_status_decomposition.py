"""Decompose the 1,342-variable attachment matrix into actionable status reasons.

Evidence-only. No identity inference, join inference, semantic promotion, or canonical
schema changes. Uses the existing master variable universe and attachment matrix as
inputs and preserves their established statuses while adding an explicit reason
category for each entity attachment state.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MASTER = DATA / "master_variable_universe.csv"
MATRIX = DATA / "variable_entity_attachment_matrix.csv"
OUT = DATA / "variable_attachment_status_decomposition.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(value: object) -> str:
    return str(value or "").strip()


def status_reason(status: str, grain: str, family: str, contract: str = "") -> str:
    status = norm(status)
    grain = norm(grain)
    family = norm(family)
    contract = norm(contract)

    if status == "REVIEW":
        if contract:
            return "REVIEW_EXISTING_RELATIONSHIP_CONTRACT_REQUIRES_EVIDENCE"
        if grain in {"team_match", "player_match", "player_season", "squad"}:
            return "REVIEW_GRAIN_SPECIFIC_IDENTITY_OR_TEMPORAL_EVIDENCE"
        return "REVIEW_SOURCE_OR_ENTITY_SCOPE"

    if status == "NOT_ESTABLISHED":
        if grain == "sample_payload":
            return "NOT_DIRECT_ENTITY_GRAIN"
        if grain in {"event", "fixture", "team", "player", "player_match", "player_season", "team_match", "squad"}:
            return "NOT_ESTABLISHED_IDENTITY_OR_RELATIONSHIP_ROUTE"
        return "NOT_ESTABLISHED_SOURCE_SCOPE"

    return "UNCLASSIFIED_STATUS"


def main() -> None:
    master = read_csv(MASTER)
    matrix = read_csv(MATRIX)
    master_names = {norm(r.get("field_name")) for r in master}
    matrix_by_name = {norm(r.get("field_name")): r for r in matrix}

    rows: list[dict[str, str]] = []
    for name in sorted(master_names):
        m = matrix_by_name.get(name, {})
        grain = norm(m.get("grain"))
        family = norm(m.get("family"))
        player_status = norm(m.get("player_status"))
        fixture_status = norm(m.get("fixture_status"))
        team_status = norm(m.get("team_club_status")) or norm(m.get("team_status"))
        contract = norm(m.get("relationship_contract"))
        rows.append({
            "field_name": name,
            "source_surface": norm(m.get("source_surface")),
            "resource": norm(m.get("resource")),
            "grain": grain,
            "family": family,
            "player_status": player_status,
            "player_reason": status_reason(player_status, grain, family, contract),
            "fixture_status": fixture_status,
            "fixture_reason": status_reason(fixture_status, grain, family, contract),
            "team_club_status": team_status,
            "team_club_reason": status_reason(team_status, grain, family, contract),
            "relationship_contract": contract,
            "identity_route": norm(m.get("identity_route")),
            "temporal_route": norm(m.get("temporal_route")),
        })

    fields = list(rows[0]) if rows else []
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("FRL VARIABLE ATTACHMENT STATUS DECOMPOSITION")
    print("=" * 100)
    print(f"Variables reviewed: {len(rows)}")
    print()
    for label, key in (
        ("PLAYER REASONS", "player_reason"),
        ("FIXTURE REASONS", "fixture_reason"),
        ("TEAM / CLUB REASONS", "team_club_reason"),
    ):
        print(label)
        counts = Counter(r[key] for r in rows)
        for reason, count in counts.most_common():
            print(f"  {count:5}  {reason}")
        print()

    print(f"Output: {OUT}")
    print("Evidence-only status decomposition; no inferred attachment and no canonical promotion.")


if __name__ == "__main__":
    main()
