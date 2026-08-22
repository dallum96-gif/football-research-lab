"""Triage FPL bootstrap variables that are absent from both current and historical layers.

Read-only. This script proposes object-family candidates from explicit JSON path structure
but never promotes a grain or canonical meaning.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RECON = ROOT / "data" / "fpl_source_layer_reconciliation.csv"
OUTPUT = ROOT / "data" / "neither_fpl_bootstrap_triage.csv"

KNOWN_FAMILIES = {
    "elements": "player",
    "teams": "team",
    "events": "gameweek",
    "element_types": "position_type",
    "phases": "phase",
    "chips": "gameweek",
    "game_settings": "game_settings",
    "game_config": "game_config",
    "scoring": "scoring_rules",
    "settings": "settings",
    "settings": "settings",
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def path_root(field_name: str) -> str:
    text = (field_name or "").replace("[]", "")
    return text.split(".", 1)[0]


def triage(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        if row.get("source_layer_state") != "NEITHER":
            continue
        field = row.get("field_name", "")
        root = path_root(field)
        candidate = KNOWN_FAMILIES.get(root, "")
        if candidate:
            basis = "explicit bootstrap JSON path root maps to a known FPL object family"
            status = "OBJECT_FAMILY_CANDIDATE"
        else:
            basis = "bootstrap JSON path root is not in the explicit known-family map"
            status = "UNKNOWN_BOOTSTRAP_ROOT"
        out.append({
            "field_name": field,
            "resource": row.get("resource", ""),
            "field_type": row.get("field_type", ""),
            "path_root": root,
            "object_family_candidate": candidate,
            "triage_status": status,
            "triage_basis": basis,
            "current_raw_found": row.get("current_raw_found", ""),
            "historical_found": row.get("historical_found", ""),
        })
    return out


def run() -> int:
    rows = triage(load_csv(RECON))
    if not rows:
        raise ValueError("No NEITHER-layer FPL bootstrap rows found.")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    status_counts = Counter(r["triage_status"] for r in rows)
    root_counts = Counter(r["path_root"] for r in rows)
    print("FRL NEITHER-LAYER FPL BOOTSTRAP TRIAGE")
    print("=" * 80)
    print(f"NEITHER-layer FPL bootstrap fields inspected: {len(rows)}")
    print("TRIAGE STATUS")
    for key, count in status_counts.most_common():
        print(f"  {key:28s} {count}")
    print("PATH ROOTS")
    for key, count in root_counts.most_common():
        print(f"  {key:28s} {count}")
    print(f"Output: {OUTPUT}")
    print("Candidate-family metadata only; no grain or canonical promotion.")
    return len(rows)


if __name__ == "__main__":
    run()
