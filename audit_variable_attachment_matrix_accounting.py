from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

MASTER_CANDIDATES = [
    DATA / "master_variable_universe.csv",
    DATA / "frl_variable_dictionary.csv",
    DATA / "variable_entity_relationship_coverage.csv",
]
MATRIX = DATA / "variable_entity_attachment_matrix.csv"
OUT = DATA / "variable_attachment_matrix_accounting.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def find_master() -> Path:
    for p in MASTER_CANDIDATES:
        if p.is_file():
            rows = read_csv(p)
            if rows and "field_name" in rows[0]:
                return p
    raise FileNotFoundError("No usable master variable universe found")


def main() -> None:
    master_path = find_master()
    master = read_csv(master_path)
    matrix = read_csv(MATRIX)

    master_fields = {r.get("field_name", "").strip() for r in master if r.get("field_name", "").strip()}
    matrix_fields = {r.get("field_name", "").strip() for r in matrix if r.get("field_name", "").strip()}

    missing = sorted(master_fields - matrix_fields)
    represented = sorted(master_fields & matrix_fields)
    extras = sorted(matrix_fields - master_fields)

    rows = []
    for field in missing:
        rows.append({
            "field_name": field,
            "status": "NOT_REPRESENTED",
            "master_present": "TRUE",
            "matrix_present": "FALSE",
        })
    for field in extras:
        rows.append({
            "field_name": field,
            "status": "MATRIX_EXTRA",
            "master_present": "FALSE",
            "matrix_present": "TRUE",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["field_name", "status", "master_present", "matrix_present"])
        writer.writeheader()
        writer.writerows(rows)

    print("FRL VARIABLE ATTACHMENT MATRIX ACCOUNTING")
    print("=" * 100)
    print(f"Master source: {master_path}")
    print(f"Master variables: {len(master_fields)}")
    print(f"Matrix represented: {len(represented)}")
    print(f"Matrix missing: {len(missing)}")
    print(f"Matrix extras: {len(extras)}")
    print()
    print("MISSING FROM MATRIX")
    if missing:
        print("  " + ", ".join(missing))
    else:
        print("  NONE")
    print()
    print("EXTRA IN MATRIX")
    if extras:
        print("  " + ", ".join(extras))
    else:
        print("  NONE")
    print(f"\nOutput: {OUT}")
    print("Evidence-only accounting; no inferred attachment and no canonical promotion.")


if __name__ == "__main__":
    main()
