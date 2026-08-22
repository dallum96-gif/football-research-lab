"""Inspect the finite NEITHER-layer FPL game_config field frontier.

Read-only discovery. Groups the exact unresolved game_config paths by their
sub-structure and field type. Does not promote grain or semantic/canonical status.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RECON = ROOT / "data" / "fpl_source_layer_reconciliation.csv"
OUTPUT = ROOT / "data" / "neither_fpl_game_config_inspection.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def substructure(field_name: str) -> str:
    text = (field_name or "").replace("[]", "")
    parts = text.split(".")
    return parts[1] if len(parts) > 1 else ""


def inspect(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        if row.get("source_layer_state") != "NEITHER":
            continue
        field = row.get("field_name", "")
        if not field.startswith("game_config"):
            continue
        out.append({
            "field_name": field,
            "terminal_field": row.get("field_name", "").split(".")[-1],
            "substructure": substructure(field),
            "resource": row.get("resource", ""),
            "field_type": row.get("field_type", ""),
            "current_raw_found": row.get("current_raw_found", ""),
            "historical_found": row.get("historical_found", ""),
            "review_status": "OPEN",
            "candidate_role": "",
            "resolution": "",
            "evidence_required": "Inspect raw/bootstrap provenance and determine whether this is configuration, scoring, or research-variable metadata.",
        })
    return out


def run() -> int:
    rows = inspect(load_csv(RECON))
    if not rows:
        raise ValueError("No NEITHER-layer game_config rows found.")
    rows.sort(key=lambda r: (r["substructure"], r["field_name"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print("FRL NEITHER-LAYER FPL GAME_CONFIG INSPECTION")
    print("=" * 80)
    print(f"game_config fields inspected: {len(rows)}")
    print("SUBSTRUCTURE")
    counts = Counter(r["substructure"] for r in rows)
    for key, count in counts.most_common():
        print(f"  {key:28s} {count}")
    print("FIELD TYPE")
    types = Counter(r["field_type"] for r in rows)
    for key, count in types.most_common():
        print(f"  {key:28s} {count}")
    print(f"Output: {OUTPUT}")
    print("Configuration-role metadata only; no grain or canonical promotion.")
    return len(rows)


if __name__ == "__main__":
    run()
