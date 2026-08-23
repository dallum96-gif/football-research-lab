"""Resolve structurally-unmapped FPL variables from the upstream variable registry.

This is a structural reconciliation only. It does not promote semantic meaning or
create canonical identities. Exact source-field matches recover the source dataset
grain; JSON dot-paths are normalised to their terminal field name for comparison.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "data" / "unmapped_variable_review_queue.csv"
UPSTREAM = ROOT / "upstream_variable_universe.csv"
OUTPUT = ROOT / "data" / "unmapped_variable_resolution_fpl.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def terminal_name(field_name: str) -> str:
    text = str(field_name or "").replace("[]", "")
    return text.split(".")[-1]


def resolve(queue_rows: list[dict[str, str]], upstream_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    exact: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in upstream_rows:
        if row.get("source_family") != "FPL API":
            continue
        variable = terminal_name(row.get("variable", ""))
        grain = row.get("dataset_grain", "")
        key = (variable, grain)
        exact.setdefault(key, []).append(row)

    out: list[dict[str, str]] = []
    for row in queue_rows:
        if row.get("source_surface") != "fpl":
            continue
        field = terminal_name(row.get("field_name", ""))
        candidates = [u for (variable, _grain), rows in exact.items() if variable == field for u in rows]
        grains = sorted({c.get("dataset_grain", "") for c in candidates if c.get("dataset_grain")})
        if len(grains) == 1:
            resolved_grain = grains[0]
            status = "STRUCTURALLY_RESOLVED"
            basis = "terminal field-name match in FPL upstream variable registry"
        elif len(grains) > 1:
            resolved_grain = "UNMAPPED_REVIEW"
            status = "AMBIGUOUS_UPSTREAM_GRAIN"
            basis = "terminal field-name match exists at multiple upstream grains"
        else:
            resolved_grain = "UNMAPPED_REVIEW"
            status = "NO_UPSTREAM_REGISTRY_MATCH"
            basis = "no terminal field-name match in FPL upstream variable registry"

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
    rows = resolve(load_csv(QUEUE), load_csv(UPSTREAM))
    if not rows:
        raise ValueError("No unresolved FPL rows found in queue.")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["resolution_status"] for row in rows)
    print("FRL UNMAPPED FPL STRUCTURAL RESOLUTION")
    print("=" * 80)
    print(f"FPL unresolved rows inspected: {len(rows)}")
    print(f"  STRUCTURALLY_RESOLVED      {counts['STRUCTURALLY_RESOLVED']}")
    print(f"  AMBIGUOUS_UPSTREAM_GRAIN   {counts['AMBIGUOUS_UPSTREAM_GRAIN']}")
    print(f"  NO_UPSTREAM_REGISTRY_MATCH {counts['NO_UPSTREAM_REGISTRY_MATCH']}")
    print(f"Output: {OUTPUT}")
    print("Exact upstream registry evidence only; no semantic/canonical promotion.")
