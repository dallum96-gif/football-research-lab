from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "data" / "audits" / "team_match_capability_queue" / "team_match_capability_queue.csv"
DEFAULT_V1 = ROOT / "data" / "team_match_semantic_promotion_batch_v1.json"
DEFAULT_V2 = ROOT / "data" / "team_match_semantic_promotion_batch_v2.json"
DEFAULT_V3 = ROOT / "data" / "team_match_semantic_promotion_batch_v3.json"
DEFAULT_EVIDENCE_V1 = ROOT / "data" / "team_match_semantic_evidence_v1.json"
DEFAULT_EVIDENCE_V2 = ROOT / "data" / "team_match_semantic_evidence_v2.json"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "audits" / "team_match_post_v3_evidence_matrix"


CRYPTIC_TOKENS = (
    "att", "ibox", "obox", "obx", "ibx", "poss", "zone", "putthrough",
    "ontarget", "cmiss", "svhigh", "svlow", "obxd", "pen", "fk",
)


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
    if any(token in low for token in CRYPTIC_TOKENS):
        return "LOW_OR_MEDIUM_DIRECT_DEFINITION_REQUIRED"
    if re.search(r"(?:left|right|centre|center|high|low|inside|outside|own|opp)", low):
        return "MEDIUM_QUALIFIER_DEFINITION_REQUIRED"
    return "HIGH_NAME_CLARITY_NOT_SEMANTIC_PROOF"


def _coverage_shape(row: Mapping[str, object]) -> str:
    pct = _float(row.get("raw_snapshot_coverage_pct"))
    if pct is None:
        return "UNKNOWN"
    if pct >= 99.999:
        return "COMPLETE"
    if pct >= 99.0:
        return "NEAR_COMPLETE"
    if pct >= 90.0:
        return "HIGH_PARTIAL"
    return "PARTIAL"


def _support_grade(field: str, evidence_docs: Iterable[Mapping[str, object]]) -> tuple[str, str, str]:
    best_grade = "NO_EXTERNAL_EVIDENCE_RECORDED"
    label = ""
    note = ""
    rank = {
        "NO_EXTERNAL_EVIDENCE_RECORDED": 0,
        "LOW_DIRECT_DEFINITION_SUPPORT": 1,
        "MEDIUM_EXTERNAL_CONCEPT_SUPPORT": 2,
        "HIGH_EXTERNAL_CONCEPT_SUPPORT": 3,
        "HIGH_DIRECT_DEFINITION_SUPPORT": 4,
    }
    for doc in evidence_docs:
        evidence = dict((doc.get("fields") or {}).get(field) or {})
        grade = str(evidence.get("support_grade") or "NO_EXTERNAL_EVIDENCE_RECORDED")
        if rank.get(grade, 0) > rank.get(best_grade, 0):
            best_grade = grade
            label = str(evidence.get("proposed_label") or "")
            note = str(evidence.get("note") or "")
    return best_grade, label, note


def _hold_map(*manifests: Mapping[str, object]) -> dict[str, str]:
    result: dict[str, str] = {}
    for manifest in manifests:
        held = manifest.get("explicitly_held_fields") or {}
        if isinstance(held, list):
            for field in held:
                result.setdefault(str(field), "Held by an earlier controlled promotion batch pending direct semantic evidence.")
        elif isinstance(held, dict):
            for field, reason in held.items():
                result[str(field)] = str(reason)
    return result


def _relation_hint(field: str, available_fields: set[str]) -> tuple[str, str]:
    candidates: list[str] = []
    if field.startswith("successful"):
        rest = field[len("successful"):]
        candidates.extend((f"total{rest}", rest[:1].lower() + rest[1:] if rest else ""))
    if field.startswith("accurate"):
        rest = field[len("accurate"):]
        candidates.append(f"total{rest}")
    if field.startswith("effective"):
        rest = field[len("effective"):]
        candidates.append(rest[:1].lower() + rest[1:] if rest else "")
    if field.startswith("won"):
        rest = field[len("won"):]
        candidates.append(f"total{rest}")
    if field.endswith("Success"):
        candidates.append(field[:-len("Success")])
    for candidate in candidates:
        if candidate and candidate in available_fields:
            return "POTENTIAL_EMPIRICAL_RELATIONSHIP", candidate
    return "NO_SIMPLE_COUNTERPART_DETECTED", ""


def _lane(
    *,
    field: str,
    hold_reason: str,
    support_grade: str,
    coverage_shape: str,
    name_clarity: str,
    relation_hint: str,
    priority: str,
) -> str:
    low_reason = hold_reason.casefold()
    if hold_reason and ("mismatch" in low_reason or "falsif" in low_reason or "violat" in low_reason):
        return "HARD_HOLD_CONFLICT_OR_FALSIFIED_ASSUMPTION"
    if hold_reason:
        return "DIRECT_DEFINITION_HOLD"
    if support_grade.startswith("HIGH_") or support_grade.startswith("MEDIUM_"):
        return "EXTERNAL_SEMANTIC_SUPPORT_REVIEW"
    if name_clarity.startswith("HIGH_") and coverage_shape == "COMPLETE":
        return "CLEAR_COMPLETE_SOURCE_FIELD_REVIEW"
    if name_clarity.startswith("HIGH_") and coverage_shape in {"NEAR_COMPLETE", "HIGH_PARTIAL"}:
        return "COVERAGE_AWARE_CLEAR_FIELD_REVIEW"
    if relation_hint == "POTENTIAL_EMPIRICAL_RELATIONSHIP":
        return "RELATIONSHIP_AUDIT_OPPORTUNITY"
    if not name_clarity.startswith("HIGH_"):
        return "QUALIFIER_OR_CRYPTIC_DEFINITION_REVIEW"
    if priority == "P0":
        return "P0_DEEPER_SEMANTIC_REVIEW"
    if priority == "P1":
        return "P1_REVIEW"
    return "P2_REVIEW"


def build_matrix(
    queue_rows: Iterable[Mapping[str, object]],
    *,
    manifests: Iterable[Mapping[str, object]],
    evidence_docs: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    queue = [dict(row) for row in queue_rows]
    manifests_tuple = tuple(manifests)
    evidence_tuple = tuple(evidence_docs)
    holds = _hold_map(*manifests_tuple)
    available_fields = {str(row.get("source_field") or "").strip() for row in queue}

    rows: list[dict[str, object]] = []
    for source in queue:
        field = str(source.get("source_field") or "").strip()
        if not field or str(source.get("reconciliation_status") or "") != "EXISTING_SOURCE_FIELD_UNCATALOGUED":
            continue

        support, label, support_note = _support_grade(field, evidence_tuple)
        clarity = _name_clarity(field)
        coverage = _coverage_shape(source)
        relation, counterpart = _relation_hint(field, available_fields)
        hold_reason = holds.get(field, "")
        priority = str(source.get("product_priority") or "")
        lane = _lane(
            field=field,
            hold_reason=hold_reason,
            support_grade=support,
            coverage_shape=coverage,
            name_clarity=clarity,
            relation_hint=relation,
            priority=priority,
        )
        rows.append({
            "source_field": field,
            "taxonomy_category": str(source.get("taxonomy_category") or ""),
            "product_priority": priority,
            "candidate_tier": str(source.get("candidate_tier") or ""),
            "coverage_shape": coverage,
            "raw_snapshot_coverage_pct": str(source.get("raw_snapshot_coverage_pct") or ""),
            "name_clarity": clarity,
            "external_support_grade": support,
            "external_proposed_label": label,
            "external_support_note": support_note,
            "prior_hold": bool(hold_reason),
            "prior_hold_reason": hold_reason,
            "relationship_hint": relation,
            "relationship_counterpart": counterpart,
            "post_v3_review_lane": lane,
            "governance_decision": "UNREVIEWED",
            "governance_note": (
                "Post-V3 evidence triage only. The matrix separates semantic support, coverage, "
                "missingness and empirical relationship opportunities. No lane or rank promotes a field."
            ),
        })

    lane_order = {
        "EXTERNAL_SEMANTIC_SUPPORT_REVIEW": 0,
        "CLEAR_COMPLETE_SOURCE_FIELD_REVIEW": 1,
        "COVERAGE_AWARE_CLEAR_FIELD_REVIEW": 2,
        "RELATIONSHIP_AUDIT_OPPORTUNITY": 3,
        "DIRECT_DEFINITION_HOLD": 4,
        "HARD_HOLD_CONFLICT_OR_FALSIFIED_ASSUMPTION": 5,
        "P0_DEEPER_SEMANTIC_REVIEW": 6,
        "QUALIFIER_OR_CRYPTIC_DEFINITION_REVIEW": 7,
        "P1_REVIEW": 8,
        "P2_REVIEW": 9,
    }
    rows.sort(key=lambda row: (
        lane_order.get(str(row["post_v3_review_lane"]), 99),
        str(row["taxonomy_category"]).casefold(),
        str(row["source_field"]).casefold(),
    ))

    return {
        "schema_version": "1.0.0",
        "scope": "REMAINING_PACKAGED_UNCATALOGUED_TEAM_MATCH_FIELDS_AFTER_VERIFIED_V3",
        "candidate_count": len(rows),
        "lane_counts": dict(sorted(Counter(str(row["post_v3_review_lane"]) for row in rows).items())),
        "coverage_counts": dict(sorted(Counter(str(row["coverage_shape"]) for row in rows).items())),
        "support_counts": dict(sorted(Counter(str(row["external_support_grade"]) for row in rows).items())),
        "taxonomy_counts": dict(sorted(Counter(str(row["taxonomy_category"]) for row in rows).items())),
        "priority_counts": dict(sorted(Counter(str(row["product_priority"]) for row in rows).items())),
        "rows": rows,
        "interpretation": (
            "This is an evidence-task matrix for the 142 packaged-but-ungoverned team-match fields after V3. "
            "It deliberately treats coverage as one evidence dimension rather than an exposure gate and preserves prior semantic holds."
        ),
    }


OUTPUT_FIELDS = (
    "source_field", "taxonomy_category", "product_priority", "candidate_tier",
    "coverage_shape", "raw_snapshot_coverage_pct", "name_clarity",
    "external_support_grade", "external_proposed_label", "external_support_note",
    "prior_hold", "prior_hold_reason", "relationship_hint", "relationship_counterpart",
    "post_v3_review_lane", "governance_decision", "governance_note",
)


def write_matrix(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "team_match_post_v3_evidence_matrix.csv"
    json_path = output_dir / "team_match_post_v3_evidence_matrix.json"
    rows = list(result.get("rows") or [])
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in OUTPUT_FIELDS})
    json_path.write_text(json.dumps(dict(result), indent=2, ensure_ascii=False), encoding="utf-8")
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the post-V3 evidence-task matrix for remaining packaged team-match fields.")
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    queue_path = args.queue.expanduser().resolve()
    if not queue_path.is_file():
        raise SystemExit(f"Capability queue not found: {queue_path}. Run scripts/triage_team_match_capability_queue.py first.")

    result = build_matrix(
        _read_csv(queue_path),
        manifests=(_read_json(DEFAULT_V1), _read_json(DEFAULT_V2), _read_json(DEFAULT_V3)),
        evidence_docs=(_read_json(DEFAULT_EVIDENCE_V1), _read_json(DEFAULT_EVIDENCE_V2)),
    )
    csv_path, json_path = write_matrix(result, args.output_dir.expanduser().resolve())
    preview = [
        {
            "source_field": row["source_field"],
            "category": row["taxonomy_category"],
            "lane": row["post_v3_review_lane"],
            "coverage": row["coverage_shape"],
            "external_support": row["external_support_grade"],
            "counterpart": row["relationship_counterpart"],
        }
        for row in list(result["rows"])[:30]
    ]
    print(json.dumps({
        "candidate_count": result["candidate_count"],
        "lane_counts": result["lane_counts"],
        "coverage_counts": result["coverage_counts"],
        "support_counts": result["support_counts"],
        "taxonomy_counts": result["taxonomy_counts"],
        "priority_counts": result["priority_counts"],
        "first_30": preview,
        "csv_output": str(csv_path),
        "json_output": str(json_path),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
