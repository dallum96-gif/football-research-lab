"""Build a deduplicated FRL master variable-universe inventory.

This is intentionally discovery-oriented. It combines:
1. the empirical FRL source catalog;
2. previously discovered upstream candidates;
3. observed keys from optional JSON payload samples.

It does NOT infer semantic equivalence merely from matching field names.
The master key is source_surface + resource + field_name + grain.

JSON samples may be supplied as local files/directories with --json-root.
This allows raw upstream payloads to be preserved locally and then enumerated
without repeatedly requesting the source.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from source_field_catalog import build_catalog

ROOT = Path(__file__).resolve().parent
UPSTREAM_CSV = ROOT / "upstream_variable_universe.csv"
DEFAULT_OUT = ROOT / "data" / "master_variable_universe.csv"


def flatten_keys(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            kind = "object" if isinstance(child, (dict, list)) else type(child).__name__
            rows.append((path, kind))
            if isinstance(child, dict):
                rows.extend(flatten_keys(child, path))
            elif isinstance(child, list) and child and isinstance(child[0], dict):
                rows.extend(flatten_keys(child[0], f"{path}[]"))
    return rows


def _json_resource(path: Path, json_root: Path) -> tuple[str, str]:
    """Normalize sample paths to source/resource families, not sample IDs."""
    relative = path.relative_to(json_root)
    parts = relative.parts
    if len(parts) >= 2:
        source = parts[0]
        family = parts[1]
        # e.g. pulselive/match-855174/snapshot.json -> pulselive/match
        if "-" in family and family.split("-", 1)[0] in {
            "match", "event", "player", "team", "season", "element"
        }:
            family = family.split("-", 1)[0]
        return source, family
    return "local_json", path.parent.name


def read_upstream_candidates() -> list[dict[str, str]]:
    if not UPSTREAM_CSV.exists():
        return []
    with UPSTREAM_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [
        {
            "source_surface": row.get("source_surface") or row.get("surface") or "upstream",
            "resource": row.get("resource") or row.get("source_resource") or "unknown",
            "grain": row.get("grain") or "unknown",
            "field_name": row.get("source_field") or row.get("field_name") or "",
            "field_type": row.get("field_type") or "unknown",
            "status": row.get("status") or row.get("decision") or "UPSTREAM_CANDIDATE",
            "notes": row.get("notes") or "",
        }
        for row in rows
        if (row.get("source_field") or row.get("field_name"))
    ]


def read_json_samples(json_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not json_root.exists():
        return rows
    for path in sorted(json_root.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - discovery tooling should fail soft
            source, resource = _json_resource(path, json_root)
            rows.append({
                "source_surface": source,
                "resource": resource,
                "grain": "unknown",
                "field_name": "",
                "field_type": "",
                "status": "UNREADABLE_JSON",
                "notes": f"{path}: {exc}",
            })
            continue
        source, resource = _json_resource(path, json_root)
        for field_name, field_type in flatten_keys(payload):
            rows.append({
                "source_surface": source,
                "resource": resource,
                "grain": "sample_payload",
                "field_name": field_name,
                "field_type": field_type,
                "status": "OBSERVED_IN_RAW_PAYLOAD",
                "notes": str(path.relative_to(json_root)),
            })
    return rows


def local_catalog_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in build_catalog():
        rows.append({
            "source_surface": "FRL_LOCAL_CSV",
            "resource": row["family"],
            "grain": row["family"],
            "field_name": row["source_field"],
            "field_type": "unknown",
            "status": row["registry_status"],
            "notes": (
                f"coverage={row['coverage_class']}; "
                f"seasons={row['seasons_present']}/{row['seasons_total']}"
            ),
        })
    return rows


def dedupe(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str, str], dict[str, str]] = {}
    statuses: defaultdict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    notes: defaultdict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    types: defaultdict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    for row in rows:
        key = (
            row["source_surface"],
            row["resource"],
            row["grain"],
            row["field_name"],
        )
        grouped.setdefault(key, row.copy())
        statuses[key].add(row.get("status", ""))
        if row.get("notes"):
            notes[key].append(row["notes"])
        if row.get("field_type"):
            types[key].add(row["field_type"])
    output: list[dict[str, str]] = []
    for key in sorted(grouped):
        row = grouped[key]
        row["statuses_seen"] = ";".join(sorted(s for s in statuses[key] if s))
        row["types_seen"] = ";".join(sorted(t for t in types[key] if t))
        row["notes"] = " | ".join(dict.fromkeys(notes[key]))
        output.append(row)
    return output


def run(json_root: Path | None = None, output: Path = DEFAULT_OUT) -> tuple[int, int]:
    rows = local_catalog_rows()
    rows.extend(read_upstream_candidates())
    if json_root:
        rows.extend(read_json_samples(json_root))
    final = dedupe(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "source_surface",
        "resource",
        "grain",
        "field_name",
        "field_type",
        "status",
        "statuses_seen",
        "types_seen",
        "notes",
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(final)
    return len(final), len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-root", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    unique_count, observed_count = run(args.json_root, args.output)
    print("FRL MASTER VARIABLE UNIVERSE ENUMERATION")
    print("READ ONLY DISCOVERY AUDIT - OUTPUT FILE IS THE INVENTORY")
    print("=" * 90)
    print(f"Observed source entries: {observed_count}")
    print(f"Deduplicated source variables: {unique_count}")
    print(f"Output: {args.output}")
    print("")
    print("COUNTING RULE")
    print("- Same field name on different resource/grain surfaces is kept distinct.")
    print("- Repeated observations of the same source field are deduplicated.")
    print("- Semantic equivalence is NOT assumed from matching names alone.")
    print("- Nested JSON properties are enumerated as dot-path fields when samples exist.")


if __name__ == "__main__":
    main()
