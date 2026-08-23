"""Build the FRL 1,414-variable entity attachment matrix.

Evidence-only audit. This consolidates existing variable-universe, grain and
relationship evidence into one row per variable without inventing joins or
promoting any identity relationship.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

FILES = {
    "master": DATA / "master_variable_universe.csv",
    "dictionary": DATA / "frl_variable_dictionary.csv",
    "coverage": DATA / "variable_entity_relationship_coverage.csv",
    "matrix": DATA / "variable_entity_relationship_matrix.csv",
}

OUT = DATA / "variable_entity_attachment_matrix.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = (row.get("field_name") or row.get("variable") or "").strip()
        if not key:
            continue
        out.setdefault(key, row)
    return out


def entity_status(value: str, *, positive: set[str], review: set[str]) -> str:
    value = (value or "").strip()
    if value in positive:
        return "VERIFIED"
    if value in review:
        return "REVIEW"
    return "NOT_ESTABLISHED"


def main() -> None:
    master_rows = read_csv(FILES["master"])
    if not master_rows:
        raise SystemExit(f"Missing master variable universe: {FILES['master']}")

    dictionary = index(read_csv(FILES["dictionary"]))
    coverage = index(read_csv(FILES["coverage"]))
    matrix = index(read_csv(FILES["matrix"]))

    fields = sorted({(r.get("field_name") or "").strip() for r in master_rows if (r.get("field_name") or "").strip()})

    positive_fixture = {
        "FIXTURE_VERIFIED",
        "ONLY_FIXTURE_VERIFIED",
        "FIXTURE_CLUB_VERIFIED",
        "PLAYER_FIXTURE_VERIFIED",
    }
    positive_team = {"FIXTURE_CLUB_VERIFIED"}
    positive_player = {"ONLY_PLAYER_VERIFIED", "PLAYER_FIXTURE_VERIFIED"}
    review = {"RELATIONSHIP_METADATA_PRESENT_REVIEW", "NO_DIRECT_ENTITY_SCOPE", "REVIEW", "unmapped_review"}

    rows: list[dict[str, str]] = []
    for field in fields:
        d = dictionary.get(field, {})
        c = coverage.get(field, {})
        m = matrix.get(field, {})

        grain = (d.get("grain") or m.get("grain") or "").strip()
        relationship_kind = (d.get("relationship_kind") or "").strip()
        identity_contract = (d.get("identity_contract") or "").strip()
        source_identity_required = (d.get("source_identity_required") or "").strip()
        attachment = (m.get("attachment_status") or "").strip()

        player = entity_status(attachment, positive=positive_player, review=review)
        team = entity_status(attachment, positive=positive_team, review=review)
        fixture = entity_status(attachment, positive=positive_fixture, review=review)

        # Direct-grain evidence is not itself a join. It is only a supporting
        # status when the existing matrix provides no attachment category.
        if attachment == "" and grain in {"player_match", "player_season", "player"}:
            player = "REVIEW"
        if attachment == "" and grain in {"team_match"}:
            team = "REVIEW"
            fixture = "REVIEW"
        if attachment == "" and grain == "fixture":
            fixture = "REVIEW"
        if attachment == "" and grain == "team":
            team = "REVIEW"

        rows.append({
            "field_name": field,
            "source_surface": d.get("source_surface", ""),
            "resource": d.get("resource", ""),
            "grain": grain,
            "field_type": d.get("field_type", ""),
            "semantic_status": d.get("semantic_status", ""),
            "relationship_kind": relationship_kind,
            "identity_contract": identity_contract,
            "source_identity_required": source_identity_required,
            "player_attachment_status": player,
            "fixture_attachment_status": fixture,
            "team_attachment_status": team,
            "matrix_attachment_status": attachment,
            "coverage_player_status": c.get("player_status", ""),
            "coverage_fixture_status": c.get("fixture_status", ""),
            "coverage_club_status": c.get("club_status", ""),
            "attachment_basis": m.get("attachment_basis", "") or m.get("reason", ""),
            "provenance_requirement": "SOURCE_ID_REQUIRED" if source_identity_required.upper() == "TRUE" else "SOURCE_LINEAGE_REQUIRED",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys()) if rows else ["field_name"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    from collections import Counter
    print("FRL VARIABLE -> ENTITY ATTACHMENT MATRIX")
    print("=" * 100)
    print(f"Variables represented: {len(rows)}")
    print()
    for label, key in (("PLAYER", "player_attachment_status"), ("FIXTURE", "fixture_attachment_status"), ("TEAM / CLUB", "team_attachment_status")):
        counts = Counter(r[key] for r in rows)
        print(label)
        for status, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {count:5d}  {status}")
        print()

    print("GRAINS")
    counts = Counter(r["grain"] or "UNSPECIFIED" for r in rows)
    for grain, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {count:5d}  {grain}")

    print()
    print(f"Output: {OUT}")
    print("Evidence-only attachment matrix; no inferred joins and no canonical promotion.")


if __name__ == "__main__":
    main()
