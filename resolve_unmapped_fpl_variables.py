"""Resolve structurally-unmapped FPL variables from the upstream variable registry.

This is a structural reconciliation only. It does not promote semantic meaning or
create canonical identities. Exact field-name matches against the upstream registry
are used to recover the source dataset grain (player/team/fixture/etc.).
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "data" / "unmapped_variable_review_queue.csv"
UPSTREAM = ROOT / "upstream_variable_universe.csv"
OUTPUT = ROOT / "data" / "unmapped_variable_resolution_fpl.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def resolve(queue_rows: list[dict[str, str]], upstream_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    exact: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in upstream_rows:
        if row.get("source_family") != "FPL API":
            continue
        key = (row.get("variable", ""), row.get("dataset_grain", ""))
        exact.setdefault(key, []).append(row)

    out: list[dict[str, str]] = []
    for row in queue_rows:
        if row.get("source_surface") != "fpl":
            continue
        field = row.get("field_name", "")
        candidates = [u for (variable, _grain), rows in exact.items() if variable == field for u in rows]
        grains = sorted({c.get("dataset_grain", "") for c in candidates if c.get("dataset_grain")})
        if len(grains) == 1:
            resolved_grain = grains[0]
            status = "STRUCTURALLY_RESOLVED"
            basis = "exact field-name match in FPL upstream variable registry"
        elif len(grains) > 1:
            resolved_grain = "UNMAPPED_REVIEW"
            status = "AMBIGUOUS_UPSTREAM_GRAIN"
            basis = "exact field-name match exists at multiple upstream grains"
        else:
            resolved_grain = "UNMAPPED_REVIEW"
            status = "NO_UPSTREAM_REGISTRY_MATCH"
            basis = "no exact field-name match in FPL upstream variable registry"

        base = dict(row)
        base.update({
            "resolved_grain": resolved_grain,
            "resolution_status": status,
            "resolution_basis": basis,
            "upstream_matches": ";".join(grains),
        })
        out.append(base)
    return out


def run(queue_path: Path = QUEUE, upstream_path: Path = UPSTREAM, output_path: Path = OUTPUT) -> int:
    queue_rows = load_csv(queue_path)
    upstream_rows = load_csv(upstream_path)
    rows = resolve(queue_rows, upstream_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No unresolved FPL rows found in queue.")
    columns = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    count = run()
    print("FRL UNMAPPED FPL STRUCTURAL RESOLUTION")
    print("=" * 80)
    print(f"FPL unresolved rows inspected: {count}")
    print(f"Output: {OUTPUT}")
    print("Exact upstream registry evidence only; no semantic/canonical promotion.")
