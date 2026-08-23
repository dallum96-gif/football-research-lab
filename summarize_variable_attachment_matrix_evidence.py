"""Summarize existing evidence columns in the variable attachment matrix.

No joins, inference, or canonical promotion. The script only groups the
already-materialized matrix rows by the matrix's own status/basis/contract
fields so the 1,342-variable frontier becomes interpretable.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MATRIX = DATA / "variable_entity_attachment_matrix.csv"
OUT = DATA / "variable_attachment_matrix_evidence_summary.csv"


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader), reader.fieldnames or []


def norm(value: object) -> str:
    return str(value or "").strip()


def bucket(value: str) -> str:
    return value if value else "UNSPECIFIED"


def main() -> None:
    if not MATRIX.is_file():
        raise SystemExit(f"Missing matrix: {MATRIX}")

    rows, columns = read_rows(MATRIX)
    print("FRL VARIABLE ATTACHMENT MATRIX EVIDENCE SUMMARY")
    print("=" * 100)
    print(f"Variables reviewed: {len(rows)}")
    print("MATRIX COLUMNS")
    for col in columns:
        print(f"  {col}")

    status_fields = {
        "PLAYER": "player_attachment_status",
        "FIXTURE": "fixture_attachment_status",
        "TEAM": "team_attachment_status",
    }
    coverage_fields = {
        "PLAYER": "coverage_player_status",
        "FIXTURE": "coverage_fixture_status",
        "TEAM": "coverage_club_status",
    }

    for entity in status_fields:
        print(f"\n{entity} ATTACHMENT STATUS")
        counter = Counter(bucket(norm(row.get(status_fields[entity]))) for row in rows)
        for key, count in counter.most_common():
            print(f"  {count:4}  {key}")

        print(f"{entity} COVERAGE STATUS")
        counter = Counter(bucket(norm(row.get(coverage_fields[entity]))) for row in rows)
        for key, count in counter.most_common():
            print(f"  {count:4}  {key}")

    for field, title in [
        ("grain", "GRAIN"),
        ("resource", "RESOURCE"),
        ("relationship_kind", "RELATIONSHIP KIND"),
        ("identity_contract", "IDENTITY CONTRACT"),
        ("attachment_basis", "ATTACHMENT BASIS"),
        ("provenance_requirement", "PROVENANCE REQUIREMENT"),
        ("semantic_status", "SEMANTIC STATUS"),
        ("source_identity_required", "SOURCE IDENTITY REQUIRED"),
        ("matrix_attachment_status", "MATRIX ATTACHMENT STATUS"),
    ]:
        print(f"\n{title}")
        counter = Counter(bucket(norm(row.get(field))) for row in rows)
        for key, count in counter.most_common():
            print(f"  {count:4}  {key}")

    # Compact evidence combination counts by entity. These are observed
    # combinations, not interpretations.
    for entity in status_fields:
        print(f"\n{entity} STATUS × COVERAGE × BASIS")
        combo = Counter(
            (
                bucket(norm(row.get(status_fields[entity]))),
                bucket(norm(row.get(coverage_fields[entity]))),
                bucket(norm(row.get("attachment_basis"))),
            )
            for row in rows
        )
        for (status, coverage, basis), count in combo.most_common(20):
            print(f"  {count:4}  status={status} | coverage={coverage} | basis={basis}")

    # Preserve the full row-level matrix with no new columns/joins; simply
    # copy it to a named evidence-summary artifact for downstream inspection.
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nOutput: {OUT}")
    print("Evidence-only summary of existing matrix fields; no inferred attachment and no canonical promotion.")


if __name__ == "__main__":
    main()
