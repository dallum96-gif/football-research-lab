"""Decompose generic sample-payload variables by observed JSON path/context.

This audit does not promote semantics. It replaces the generic sample_payload grain
with the most defensible observed object context, while failing closed when the
path does not provide enough evidence to assign a canonical FRL grain.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "master_variable_universe.csv"
OUTPUT = ROOT / "data" / "master_variable_universe_decomposed.csv"

GRAIN_BY_CONTEXT = {
    "player_match": "player_match",
    "team_match": "team_match",
    "player_season": "player_season",
    "squad": "squad",
    "fixture": "fixture",
    "match": "fixture",
    "event": "event",
    "player": "player",
    "team": "team",
    "competition": "competition",
    "season": "season",
    "gameweek": "gameweek",
    "standings": "standings",
}


def infer_context(field_name: str, resource: str, grain: str, note: str) -> tuple[str, str]:
    text = " ".join((field_name, resource, grain, note)).lower()
    path = field_name.lower()

    # Strongest evidence: explicit nested object/path markers.
    for marker, grain_name in GRAIN_BY_CONTEXT.items():
        if f".{marker}." in path or path.startswith(f"{marker}.") or f"/{marker}/" in path:
            return grain_name, f"path marker: {marker}"

    # Resource-level evidence can establish a source grain.
    for marker, grain_name in GRAIN_BY_CONTEXT.items():
        if marker in resource.lower() or f" {marker} " in text:
            return grain_name, f"resource/context marker: {marker}"

    # Conservative field-name heuristics only for obvious structures.
    if any(token in path for token in ("player", "element", "playerid", "player_id")):
        if any(token in text for token in ("fixture", "match", "event")):
            return "player_match", "field/context indicates player-match observation"
        return "player", "field/context indicates player entity"
    if any(token in path for token in ("team", "home_team", "away_team")):
        if any(token in text for token in ("fixture", "match")):
            return "team_match", "field/context indicates team-fixture observation"
        return "team", "field/context indicates team entity"

    # Do not guess. Preserve the prior label where it is already specific.
    if grain and grain != "sample_payload":
        return grain, "pre-existing specific grain"

    return "UNMAPPED_REVIEW", "insufficient structural evidence"


def run(input_path: Path = INPUT, output_path: Path = OUTPUT) -> int:
    with input_path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    columns = list(rows[0].keys()) + ["decomposed_grain", "decomposition_basis"] if rows else []
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            grain, basis = infer_context(
                row.get("field_name", ""),
                row.get("resource", ""),
                row.get("grain", ""),
                row.get("notes", ""),
            )
            row = dict(row)
            row["decomposed_grain"] = grain
            row["decomposition_basis"] = basis
            writer.writerow(row)

    return len(rows)


if __name__ == "__main__":
    count = run()
    print("FRL SAMPLE-PAYLOAD GRAIN DECOMPOSITION")
    print("=" * 80)
    print(f"Variables inspected: {count}")
    print(f"Output: {OUTPUT}")
    print("Unknown structure remains UNMAPPED_REVIEW; no canonical relationship is created.")
