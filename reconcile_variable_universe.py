"""Reconcile a mapped FRL variable baseline against a broader source inventory.

This utility is intentionally conservative. It does not decide semantic
 equivalence from names alone. It produces a reconciliation table that can be
 reviewed and promoted into the authoritative FRL variable registry.

Supported inputs:
- CSV files
- JSON arrays of objects

Expected/recognised columns (aliases are accepted):
- source_family / family
- source_field / field / variable
- candidate_name / name
- canonical_variable / frl_field
- natural_grain / grain
- semantic_status / status
- coverage / seasons

Usage example:
    python reconcile_variable_universe.py \
      --baseline path\\to\\477.csv \
      --universe path\\to\\universe.csv \
      --output path\\to\\variable_reconciliation.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable


ALIASES = {
    "source_family": ("source_family", "family", "provider_family"),
    "source_field": ("source_field", "field", "variable", "field_name"),
    "candidate_name": ("candidate_name", "name", "variable_name", "frl_field"),
    "canonical_variable": ("canonical_variable", "frl_field", "canonical_name"),
    "natural_grain": ("natural_grain", "grain", "observation_grain"),
    "semantic_status": ("semantic_status", "status"),
    "coverage": ("coverage", "seasons", "season_coverage"),
}


@dataclass(frozen=True)
class Row:
    source_family: str = ""
    source_field: str = ""
    candidate_name: str = ""
    canonical_variable: str = ""
    natural_grain: str = ""
    semantic_status: str = ""
    coverage: str = ""
    baseline_present: bool = False
    broad_universe_present: bool = False
    reconciliation_status: str = "SOURCE_NATIVE_UNMAPPED"
    notes: str = ""


def _first(record: dict[str, Any], names: Iterable[str]) -> str:
    for name in names:
        value = record.get(name)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def _normalise(record: dict[str, Any]) -> dict[str, str]:
    return {
        key: _first(record, aliases)
        for key, aliases in ALIASES.items()
    }


def load_records(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"JSON input must be an array of objects: {path}")
        return [_normalise(dict(item)) for item in data]

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV input has no header: {path}")
        return [_normalise(dict(row)) for row in reader]


def key(record: dict[str, str]) -> tuple[str, str, str]:
    return (
        record["source_family"].lower(),
        record["source_field"].lower(),
        record["natural_grain"].lower(),
    )


def display_name(record: dict[str, str]) -> str:
    return record["canonical_variable"] or record["candidate_name"] or record["source_field"]


def reconcile(baseline: list[dict[str, str]], broad: list[dict[str, str]]) -> list[Row]:
    baseline_by_key: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    broad_by_key: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)

    for record in baseline:
        baseline_by_key[key(record)].append(record)
    for record in broad:
        broad_by_key[key(record)].append(record)

    all_keys = sorted(set(baseline_by_key) | set(broad_by_key))
    rows: list[Row] = []

    for item_key in all_keys:
        b_rows = baseline_by_key.get(item_key, [])
        u_rows = broad_by_key.get(item_key, [])
        representative = (u_rows or b_rows)[0]
        baseline_present = bool(b_rows)
        broad_present = bool(u_rows)

        if baseline_present and broad_present:
            status = "MAPPED_VALIDATED" if representative["semantic_status"].lower() in {
                "validated", "exposed", "retained"
            } else "MAPPED_VALIDATION_PENDING"
            notes = "Exact family + field + grain match."
        elif baseline_present:
            status = "MAPPED_VALIDATION_PENDING"
            notes = "Present in mapped baseline but absent from broad inventory supplied to reconciliation."
        else:
            status = "SOURCE_NATIVE_UNMAPPED"
            notes = "Present in broad inventory but not matched to mapped baseline."

        if len(b_rows) > 1 or len(u_rows) > 1:
            status = "DUPLICATE_SOURCE_FACET"
            notes += " Multiple records share the same reconciliation key; inspect before promotion."

        rows.append(
            Row(
                source_family=representative["source_family"],
                source_field=representative["source_field"],
                candidate_name=representative["candidate_name"],
                canonical_variable=representative["canonical_variable"],
                natural_grain=representative["natural_grain"],
                semantic_status=representative["semantic_status"],
                coverage=representative["coverage"],
                baseline_present=baseline_present,
                broad_universe_present=broad_present,
                reconciliation_status=status,
                notes=notes,
            )
        )

    # Detect canonical aliases that occur across multiple source facets.
    canonical_groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        if row.canonical_variable:
            canonical_groups[row.canonical_variable.lower()].append(index)

    mutable = list(rows)
    for canonical, indexes in canonical_groups.items():
        facets = {
            (mutable[i].source_family.lower(), mutable[i].source_field.lower(), mutable[i].natural_grain.lower())
            for i in indexes
        }
        if len(facets) > 1:
            for i in indexes:
                current = mutable[i]
                if current.reconciliation_status in {"MAPPED_VALIDATED", "MAPPED_VALIDATION_PENDING"}:
                    mutable[i] = Row(**{
                        **asdict(current),
                        "notes": (current.notes + " Canonical variable is represented by multiple source facets; preserve them separately and document equivalence.").strip(),
                    })

    return mutable


def write_csv(rows: list[Row], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()) if rows else list(asdict(Row()).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile FRL variable inventories.")
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--universe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    baseline = load_records(args.baseline)
    broad = load_records(args.universe)
    rows = reconcile(baseline, broad)
    write_csv(rows, args.output)

    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row.reconciliation_status] += 1

    print(f"Baseline input rows: {len(baseline)}")
    print(f"Broad-universe input rows: {len(broad)}")
    print(f"Reconciliation rows: {len(rows)}")
    for status in sorted(counts):
        print(f"{status}: {counts[status]}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
