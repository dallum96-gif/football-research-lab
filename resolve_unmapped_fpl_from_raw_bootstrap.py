"""Resolve unresolved FPL variables directly from captured raw bootstrap payloads.

Structural only: source-native fields are mapped to the object containing them.
No semantic/canonical promotion and no identity inference.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "data" / "unmapped_variable_review_queue.csv"
RAW = ROOT / "raw_upstream" / "fpl" / "bootstrap-static.json"
OUTPUT = ROOT / "data" / "unmapped_variable_resolution_fpl_raw.csv"

OBJECT_GRAINS = {
    "elements": "player",
    "teams": "team",
    "events": "gameweek",
    "element_stats": "bootstrap_metadata",
    "element_types": "position_type",
    "phases": "phase",
    "game_settings": "game_settings",
    "scoring": "scoring_rules",
    "settings": "settings",
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def bootstrap_field_presence(payload: dict) -> dict[str, set[str]]:
    """Return fields observed directly within each top-level bootstrap object family."""
    out: dict[str, set[str]] = {}
    for prefix, grain in OBJECT_GRAINS.items():
        value = payload.get(prefix)
        if isinstance(value, list):
            names: set[str] = set()
            for item in value:
                if isinstance(item, dict):
                    names.update(str(key) for key in item.keys())
            out[grain] = names
        elif isinstance(value, dict):
            out[grain] = {str(key) for key in value.keys()}
    return out


def resolve(queue_rows: list[dict[str, str]], payload: dict) -> list[dict[str, str]]:
    presence = bootstrap_field_presence(payload)

    # Explicit field -> object-family occurrences. A field is structurally
    # resolved only when the captured payload shows it in exactly one family.
    occurrences: dict[str, set[str]] = {}
    for grain, fields in presence.items():
        for field in fields:
            occurrences.setdefault(field, set()).add(grain)

    out: list[dict[str, str]] = []
    for row in queue_rows:
        if row.get("source_surface") != "fpl":
            continue

        field = row.get("field_name", "")
        grains = sorted(occurrences.get(field, set()))
        base = dict(row)

        if len(grains) == 1:
            base.update({
                "resolved_grain": grains[0],
                "resolution_status": "STRUCTURALLY_RESOLVED",
                "resolution_basis": "exact field-name occurrence in captured raw FPL bootstrap object family",
                "upstream_matches": ";".join(grains),
            })
        elif len(grains) > 1:
            base.update({
                "resolved_grain": "UNMAPPED_REVIEW",
                "resolution_status": "AMBIGUOUS_RAW_BOOTSTRAP_GRAIN",
                "resolution_basis": "exact field-name occurs in multiple captured bootstrap object families",
                "upstream_matches": ";".join(grains),
            })
        else:
            base.update({
                "resolved_grain": "UNMAPPED_REVIEW",
                "resolution_status": "NOT_FOUND_IN_RAW_BOOTSTRAP",
                "resolution_basis": "field not observed in captured raw bootstrap object families",
                "upstream_matches": "",
            })

        out.append(base)

    return out


def run() -> int:
    queue_rows = load_csv(QUEUE)
    if not RAW.exists():
        raise FileNotFoundError(f"Raw bootstrap payload not found: {RAW}")

    payload = json.loads(RAW.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Raw bootstrap payload is not a JSON object")

    rows = resolve(queue_rows, payload)
    if not rows:
        raise ValueError("No unresolved FPL rows found in queue")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["resolution_status"]] = counts.get(row["resolution_status"], 0) + 1

    print("FRL UNMAPPED FPL RAW-BOOTSTRAP STRUCTURAL RESOLUTION")
    print("=" * 80)
    print(f"FPL unresolved rows inspected: {len(rows)}")
    for key in (
        "STRUCTURALLY_RESOLVED",
        "AMBIGUOUS_RAW_BOOTSTRAP_GRAIN",
        "NOT_FOUND_IN_RAW_BOOTSTRAP",
    ):
        print(f"  {key:34s} {counts.get(key, 0)}")
    print(f"Output: {OUTPUT}")
    print("Captured raw payload only; no semantic/canonical promotion.")
    return len(rows)


if __name__ == "__main__":
    run()
