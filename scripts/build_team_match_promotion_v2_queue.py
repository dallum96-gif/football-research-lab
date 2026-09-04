from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = (
    ROOT / "data" / "audits" / "team_match_capability_queue" / "team_match_capability_queue.csv"
)
DEFAULT_PROMOTION_V1 = ROOT / "data" / "team_match_semantic_promotion_batch_v1.json"
DEFAULT_SEMANTIC_EVIDENCE = ROOT / "data" / "team_match_semantic_evidence_v1.json"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "audits" / "team_match_promotion_v2"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: object) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _name_clarity(field: str) -> str:
    low = field.casefold()
    cryptic = (
        "att", "ibox", "obox", "poss", "zone", "putthrough", "ontarget", "fk",
        "cmiss", "svhigh", "svlow", "obxd", "ibx", "lg",
    )
    if any(token in low for token in cryptic):
        return "MEDIUM_OR_LOW_DIRECT_DEFINITION_NEEDED"
    return "HIGH_NAME_CLARITY_NOT_SEMANTIC_PROOF"


def _missingness_lane(row: Mapping[str, object]) -> str:
    coverage = _float(row.get("raw_snapshot_coverage_pct"))
    if coverage is None:
        return "MISSINGNESS_EVIDENCE_REQUIRED"
    if coverage >= 99.999:
        return "FULL_RAW_PATH_PRESENCE_CONFIRM_BLANK_SEMANTICS"
    return "SPARSE_OR_OPTIONAL_ENCODING_REVIEW"


def _v2_lane(
    row: Mapping[str, object],
    *,
    held_fields: set[str],
    support_grade: str,
) -> str:
    field = str(row.get("source_field") or "")
    if field in held_fields:
        return "V1_HELD_DIRECT_DEFINITION_REQUIRED"

    tier = str(row.get("candidate_tier") or "")
    clarity = _name_clarity(field)
    missingness = _missingness_lane(row)

    if tier == "FIRST_PROMOTION_REVIEW_BATCH":
        if missingness.startswith("FULL_") and clarity.startswith("HIGH_"):
            if support_grade.startswith("HIGH_") or support_grade.startswith("MEDIUM_"):
                return "V2_EVIDENCE_STACK_REVIEW_NOW"
            return "V2_SEMANTIC_REVIEW_NOW"
        if missingness.startswith("FULL_"):
            return "V2_SOURCE_DEFINITION_REVIEW"
        return "V2_MISSINGNESS_FIRST"

    if tier == "P0_PROMOTION_REVIEW":
        return "V2_P0_DEEPER_REVIEW"
    if tier == "P1_PROMOTION_REVIEW":
        return "V2_P1_REVIEW"
    if tier == "P2_PROMOTION_REVIEW":
        return "V2_P2_REVIEW"
    return "V2_MANUAL_REVIEW"


def build_v2_queue(
    queue_rows: Iterable[Mapping[str, object]],
    promotion_v1: Mapping[str, object],
    semantic_evidence: Mapping[str, object],
) -> dict[str, object]:
    promoted = {str(field) for field in promotion_v1.get("promoted_fields", [])}
    held = {str(field) for field in promotion_v1.get("explicitly_held_fields", [])}
    evidence_fields = dict(semantic_evidence.get("fields") or {})

    rows: list[dict[str, object]] = []
    for source in queue_rows:
        field = str(source.get("source_field") or "").strip()
        status = str(source.get("reconciliation_status") or "")
        if not field or field in promoted:
            continue
        if status != "EXISTING_SOURCE_FIELD_UNCATALOGUED":
            continue

        evidence = dict(evidence_fields.get(field) or {})
        support_grade = str(evidence.get("support_grade") or "NO_EXTERNAL_EVIDENCE_RECORDED")
        lane = _v2_lane(source, held_fields=held, support_grade=support_grade)
        rows.append(
            {
                "source_field": field,
                "taxonomy_category": str(source.get("taxonomy_category") or ""),
                "taxonomy_secondary_category": str(
                    source.get("taxonomy_secondary_category") or ""
                ),
                "product_priority": str(source.get("product_priority") or ""),
                "candidate_tier": str(source.get("candidate_tier") or ""),
                "coverage_class": str(source.get("existing_coverage_class") or ""),
                "raw_snapshot_coverage_pct": str(
                    source.get("raw_snapshot_coverage_pct") or ""
                ),
                "raw_value_types": str(source.get("raw_value_types") or ""),
                "raw_sample_values": str(source.get("raw_sample_values") or ""),
                "semantic_name_clarity": _name_clarity(field),
                "missingness_lane": _missingness_lane(source),
                "external_support_grade": support_grade,
                "external_proposed_label": str(evidence.get("proposed_label") or ""),
                "external_evidence_note": str(evidence.get("note") or ""),
                "carried_v1_hold": field in held,
                "v2_review_lane": lane,
                "governance_decision": "UNREVIEWED",
                "governance_note": (
                    "V2 prioritisation only. No lane automatically promotes a field. "
                    "Direct semantics, aggregation, missingness and comparability still require explicit review."
                ),
            }
        )

    lane_order = {
        "V2_EVIDENCE_STACK_REVIEW_NOW": 0,
        "V2_SEMANTIC_REVIEW_NOW": 1,
        "V1_HELD_DIRECT_DEFINITION_REQUIRED": 2,
        "V2_SOURCE_DEFINITION_REVIEW": 3,
        "V2_MISSINGNESS_FIRST": 4,
        "V2_P0_DEEPER_REVIEW": 5,
        "V2_P1_REVIEW": 6,
        "V2_P2_REVIEW": 7,
        "V2_MANUAL_REVIEW": 8,
    }
    rows.sort(
        key=lambda row: (
            lane_order.get(str(row["v2_review_lane"]), 99),
            str(row["taxonomy_category"]).casefold(),
            str(row["source_field"]).casefold(),
        )
    )

    return {
        "schema_version": "1.0.0",
        "scope": "REMAINING_PACKAGED_UNCATALOGUED_TEAM_MATCH_FIELDS_AFTER_V1",
        "candidate_count": len(rows),
        "lane_counts": dict(
            sorted(Counter(str(row["v2_review_lane"]) for row in rows).items())
        ),
        "taxonomy_counts": dict(
            sorted(Counter(str(row["taxonomy_category"]) for row in rows).items())
        ),
        "priority_counts": dict(
            sorted(Counter(str(row["product_priority"]) for row in rows).items())
        ),
        "rows": rows,
        "interpretation": (
            "This queue starts after the verified V1 promotion. It ranks the remaining packaged "
            "uncatalogued team-match fields for human semantic/governance review and deliberately "
            "does not infer promotion from names, coverage, external terminology or prior invariants."
        ),
    }


OUTPUT_FIELDS = (
    "source_field",
    "taxonomy_category",
    "taxonomy_secondary_category",
    "product_priority",
    "candidate_tier",
    "coverage_class",
    "raw_snapshot_coverage_pct",
    "raw_value_types",
    "raw_sample_values",
    "semantic_name_clarity",
    "missingness_lane",
    "external_support_grade",
    "external_proposed_label",
    "external_evidence_note",
    "carried_v1_hold",
    "v2_review_lane",
    "governance_decision",
    "governance_note",
)


def write_queue(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "team_match_promotion_v2_queue.csv"
    json_path = output_dir / "team_match_promotion_v2_queue.json"
    rows = list(result.get("rows") or [])

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in OUTPUT_FIELDS})

    json_path.write_text(
        json.dumps(dict(result), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the evidence-aware V2 review queue for remaining packaged team-match fields."
    )
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--promotion-v1", type=Path, default=DEFAULT_PROMOTION_V1)
    parser.add_argument("--semantic-evidence", type=Path, default=DEFAULT_SEMANTIC_EVIDENCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    queue_path = args.queue.expanduser().resolve()
    if not queue_path.is_file():
        raise SystemExit(
            f"Capability queue not found: {queue_path}. Run scripts/triage_team_match_capability_queue.py first."
        )

    result = build_v2_queue(
        _read_csv(queue_path),
        _read_json(args.promotion_v1.expanduser().resolve()),
        _read_json(args.semantic_evidence.expanduser().resolve()),
    )
    csv_path, json_path = write_queue(result, args.output_dir.expanduser().resolve())
    preview = [
        {
            "source_field": row["source_field"],
            "category": row["taxonomy_category"],
            "lane": row["v2_review_lane"],
            "external_support": row["external_support_grade"],
        }
        for row in list(result["rows"])[:25]
    ]
    print(
        json.dumps(
            {
                "candidate_count": result["candidate_count"],
                "lane_counts": result["lane_counts"],
                "taxonomy_counts": result["taxonomy_counts"],
                "priority_counts": result["priority_counts"],
                "first_25_candidates": preview,
                "csv_output": str(csv_path),
                "json_output": str(json_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
