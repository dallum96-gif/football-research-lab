"""Validate that the FPL structural audit partitions reconcile exactly.

Read-only validator. It does not promote grain, identity, or semantic meaning.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALL_RAW = ROOT / "data" / "unmapped_variable_resolution_fpl_all_raw.csv"
AMBIGUOUS = ROOT / "data" / "ambiguous_fpl_variable_audit.csv"
AMBIGUOUS_RESOLVED = ROOT / "data" / "ambiguous_fpl_resource_context_resolution.csv"
RECON = ROOT / "data" / "fpl_source_layer_reconciliation.csv"
BOOTSTRAP_TRIAGE = ROOT / "data" / "neither_fpl_bootstrap_triage.csv"
GAME_CONFIG = ROOT / "data" / "neither_fpl_game_config_inspection.csv"


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    all_raw = load(ALL_RAW)
    ambiguous = load(AMBIGUOUS)
    ambiguous_resolved = load(AMBIGUOUS_RESOLVED)
    recon = load(RECON)
    bootstrap = load(BOOTSTRAP_TRIAGE)
    game_config = load(GAME_CONFIG)

    raw_counts = Counter(r["resolution_status"] for r in all_raw)
    context_counts = Counter(r["resolution_status"] for r in ambiguous_resolved)

    all_fields = {r["field_name"] for r in all_raw}
    ambiguous_fields = {r["field_name"] for r in ambiguous}
    expected_ambiguous = {r["field_name"] for r in all_raw if r["resolution_status"] == "AMBIGUOUS_RAW_FPL_GRAIN"}
    context_resolved_fields = {r["field_name"] for r in ambiguous_resolved if r["resolution_status"] == "STRUCTURALLY_RESOLVED"}
    context_ambiguous_fields = {r["field_name"] for r in ambiguous_resolved if r["resolution_status"] == "AMBIGUOUS_RESOURCE_CONTEXT"}
    historical_only_fields = {r["field_name"] for r in recon if r["source_layer_state"] == "HISTORICAL_PUBLISHED_ONLY"}
    neither_fields = {r["field_name"] for r in recon if r["source_layer_state"] == "NEITHER"}
    game_config_fields = {r["field_name"] for r in game_config}

    errors: list[str] = []
    if ambiguous_fields != expected_ambiguous:
        errors.append(f"ambiguity queue mismatch: audit={len(ambiguous_fields)} expected={len(expected_ambiguous)}")
    if not context_resolved_fields.issubset(expected_ambiguous):
        errors.append("resource-context resolved fields are outside current ambiguity queue")
    if not context_ambiguous_fields.issubset(expected_ambiguous):
        errors.append("resource-context unresolved fields are outside current ambiguity queue")
    if context_resolved_fields & context_ambiguous_fields:
        errors.append("resource-context resolved/unresolved sets overlap")
    if not historical_only_fields.issubset(all_fields):
        errors.append("historical-only fields are outside current all-raw universe")
    if not neither_fields.issubset(all_fields):
        errors.append("reconciliation contains fields outside current all-raw universe")
    if not game_config_fields.issubset(neither_fields):
        errors.append("game_config inspection contains fields outside current NEITHER layer")

    closed = (
        raw_counts.get("STRUCTURALLY_RESOLVED", 0)
        + len(context_resolved_fields)
        + len(historical_only_fields)
        + len(game_config_fields)
    )
    outstanding = len(context_ambiguous_fields) + (len(neither_fields) - len(game_config_fields))

    print("FRL FPL STRUCTURAL CLOSURE VALIDATOR")
    print("=" * 80)
    print(f"All-raw rows: {len(all_raw)}")
    print(f"All-raw resolved: {raw_counts.get('STRUCTURALLY_RESOLVED', 0)}")
    print(f"All-raw ambiguous: {raw_counts.get('AMBIGUOUS_RAW_FPL_GRAIN', 0)}")
    print(f"All-raw not found: {raw_counts.get('NOT_FOUND_IN_ALL_CAPTURED_RAW_FPL', 0)}")
    print(f"Context-resolved: {len(context_resolved_fields)}")
    print(f"Context-ambiguous: {len(context_ambiguous_fields)}")
    print(f"Historical-published-only: {len(historical_only_fields)}")
    print(f"NEITHER-layer fields: {len(neither_fields)}")
    print(f"game_config fields: {len(game_config_fields)}")
    print(f"Bootstrap triage rows: {len(bootstrap)}")
    print(f"Layer reconciliation rows: {len(recon)}")
    print(f"Closed/resolved partition: {closed}")
    print(f"Outstanding structural frontier: {outstanding}")

    if len(recon) != len(all_raw):
        errors.append(f"layer reconciliation cardinality mismatch: reconciliation={len(recon)} all_raw={len(all_raw)}")
    if closed + outstanding != len(all_fields):
        errors.append(f"partition mismatch: closed={closed} outstanding={outstanding} total={len(all_fields)}")

    if errors:
        print("STATUS: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("STATUS: PASS")
    print("Current derived artifacts reconcile; no semantic/canonical promotion performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
