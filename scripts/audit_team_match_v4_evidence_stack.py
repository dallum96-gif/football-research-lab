from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from source_field_catalog import SEASONS
from source_family_adapters import team_match_source_rows_for_season

DEFAULT_MATRIX = (
    ROOT
    / "data"
    / "audits"
    / "team_match_post_v3_evidence_matrix"
    / "team_match_post_v3_evidence_matrix.csv"
)
DEFAULT_EVIDENCE = ROOT / "data" / "team_match_semantic_evidence_v4.json"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "audits" / "team_match_v4_evidence_stack"

REVIEW_LANES = {
    "EXTERNAL_SEMANTIC_SUPPORT_REVIEW",
    "CLEAR_COMPLETE_SOURCE_FIELD_REVIEW",
    "COVERAGE_AWARE_CLEAR_FIELD_REVIEW",
    "RELATIONSHIP_AUDIT_OPPORTUNITY",
}

# These are source-name relationship hypotheses only. They are audited as
# empirical consistency checks and never treated as semantic proof by themselves.
EXTRA_RELATIONSHIPS = {
    "accurateKeeperThrows": "keeperThrows",
    "accurateGoalKicks": "goalKicks",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _number(value: object) -> float | None:
    if value in (None, "", "null", "None"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def relationship_rules(
    matrix_rows: Iterable[Mapping[str, object]],
    *,
    evidence_fields: set[str] | None = None,
) -> tuple[dict[str, str], ...]:
    evidence_fields = evidence_fields or set()
    rules: dict[tuple[str, str], dict[str, str]] = {}
    for row in matrix_rows:
        field = str(row.get("source_field") or "").strip()
        counterpart = str(row.get("relationship_counterpart") or "").strip()
        lane = str(row.get("post_v3_review_lane") or "")
        if not field or not counterpart:
            continue
        if lane not in REVIEW_LANES and field not in evidence_fields:
            continue
        key = (field, counterpart)
        rules[key] = {
            "rule_id": f"{field}_lte_{counterpart}",
            "child_field": field,
            "parent_field": counterpart,
            "rationale": (
                f"Source-name relationship hypothesis: {field} should not exceed {counterpart}. "
                "Passing this check is supporting evidence only."
            ),
        }

    matrix_fields = {str(row.get("source_field") or "").strip() for row in matrix_rows}
    for child, parent in EXTRA_RELATIONSHIPS.items():
        if child in matrix_fields and (child in evidence_fields or parent in matrix_fields):
            rules[(child, parent)] = {
                "rule_id": f"{child}_lte_{parent}",
                "child_field": child,
                "parent_field": parent,
                "rationale": (
                    f"External concept support plus source-name hypothesis: {child} should not exceed {parent}."
                ),
            }
    return tuple(rules.values())


def evaluate_relationships(
    rows: Iterable[Mapping[str, object]],
    *,
    rules: Sequence[Mapping[str, str]],
    season: str = "",
) -> tuple[dict[str, object], ...]:
    materialised = tuple(rows)
    results: list[dict[str, object]] = []
    for rule in rules:
        child = str(rule["child_field"])
        parent = str(rule["parent_field"])
        compared = 0
        violations = 0
        negative_rows = 0
        examples: list[dict[str, object]] = []
        for row in materialised:
            child_value = _number(row.get(child))
            parent_value = _number(row.get(parent))
            if child_value is None or parent_value is None:
                continue
            compared += 1
            if child_value < 0 or parent_value < 0:
                negative_rows += 1
            if child_value > parent_value + 1e-9:
                violations += 1
                if len(examples) < 5:
                    examples.append(
                        {
                            "fixture_id": str(row.get("frl_fixture_id") or row.get("matchId") or ""),
                            "team_id": str(row.get("team_id") or row.get("team") or ""),
                            "child": child_value,
                            "parent": parent_value,
                        }
                    )
        if compared == 0:
            status = "NO_COMPARABLE_OBSERVATIONS"
        elif violations == 0 and negative_rows == 0:
            status = "EMPIRICALLY_CONSISTENT_NO_VIOLATIONS"
        else:
            status = "REVIEW_VIOLATIONS"
        results.append(
            {
                "season": season,
                "rule_id": str(rule["rule_id"]),
                "child_field": child,
                "parent_field": parent,
                "rows_compared": compared,
                "violations": violations,
                "negative_value_rows": negative_rows,
                "status": status,
                "example_violations": examples,
                "rationale": str(rule["rationale"]),
            }
        )
    return tuple(results)


def profile_fields(
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> dict[str, dict[str, object]]:
    materialised = tuple(rows)
    profiles: dict[str, dict[str, object]] = {}
    for field in fields:
        numeric: list[float] = []
        nonblank = 0
        negative = 0
        zero = 0
        for row in materialised:
            raw = row.get(field)
            if raw not in (None, "", "null", "None"):
                nonblank += 1
            value = _number(raw)
            if value is None:
                continue
            numeric.append(value)
            if value < 0:
                negative += 1
            if abs(value) <= 1e-9:
                zero += 1
        profiles[field] = {
            "rows": len(materialised),
            "nonblank_rows": nonblank,
            "numeric_rows": len(numeric),
            "blank_rows": len(materialised) - nonblank,
            "zero_rows": zero,
            "negative_rows": negative,
            "minimum": min(numeric) if numeric else None,
            "maximum": max(numeric) if numeric else None,
            "missingness_note": "Blank remains missing unless separately governed as structural zero.",
        }
    return profiles


def build_audit(
    matrix_rows: Iterable[Mapping[str, object]],
    evidence: Mapping[str, object],
    *,
    seasons: Sequence[str] = SEASONS,
) -> dict[str, object]:
    matrix = [dict(row) for row in matrix_rows]
    evidence_rows = dict(evidence.get("fields") or {})
    evidence_fields = set(evidence_rows)
    rules = relationship_rules(matrix, evidence_fields=evidence_fields)

    matrix_by_field = {str(row.get("source_field") or ""): row for row in matrix}
    review_fields = {
        str(row.get("source_field") or "")
        for row in matrix
        if str(row.get("post_v3_review_lane") or "") in REVIEW_LANES
    }
    review_fields.update(evidence_fields)
    review_fields.discard("")

    aggregate_profiles: dict[str, dict[str, object]] = {
        field: {
            "rows": 0,
            "nonblank_rows": 0,
            "numeric_rows": 0,
            "blank_rows": 0,
            "zero_rows": 0,
            "negative_rows": 0,
            "minimum": None,
            "maximum": None,
            "missingness_note": "Blank remains missing unless separately governed as structural zero.",
        }
        for field in sorted(review_fields)
    }
    season_results: list[dict[str, object]] = []
    season_row_counts: dict[str, int] = {}

    for season in seasons:
        rows = team_match_source_rows_for_season(season)
        season_row_counts[season] = len(rows)
        season_results.extend(evaluate_relationships(rows, rules=rules, season=season))
        profiles = profile_fields(rows, sorted(review_fields))
        for field, profile in profiles.items():
            aggregate = aggregate_profiles[field]
            for key in ("rows", "nonblank_rows", "numeric_rows", "blank_rows", "zero_rows", "negative_rows"):
                aggregate[key] = int(aggregate[key]) + int(profile[key])
            for key, fn in (("minimum", min), ("maximum", max)):
                value = profile[key]
                current = aggregate[key]
                if value is None:
                    continue
                aggregate[key] = value if current is None else fn(float(current), float(value))

    relationship_summaries: list[dict[str, object]] = []
    for rule in rules:
        items = [row for row in season_results if row["rule_id"] == rule["rule_id"]]
        compared = sum(int(row["rows_compared"]) for row in items)
        violations = sum(int(row["violations"]) for row in items)
        negative = sum(int(row["negative_value_rows"]) for row in items)
        if compared == 0:
            status = "NO_COMPARABLE_OBSERVATIONS"
        elif violations == 0 and negative == 0:
            status = "DECADE_EMPIRICALLY_CONSISTENT"
        else:
            status = "DECADE_REVIEW_REQUIRED"
        examples: list[dict[str, object]] = []
        for item in items:
            for example in item.get("example_violations", []):
                if len(examples) >= 5:
                    break
                examples.append({"season": item["season"], **dict(example)})
        relationship_summaries.append(
            {
                "rule_id": str(rule["rule_id"]),
                "child_field": str(rule["child_field"]),
                "parent_field": str(rule["parent_field"]),
                "rows_compared": compared,
                "violations": violations,
                "negative_value_rows": negative,
                "status": status,
                "example_violations": examples,
            }
        )

    relationship_by_child = {str(row["child_field"]): row for row in relationship_summaries}
    candidate_rows: list[dict[str, object]] = []
    for field in sorted(review_fields):
        matrix_row = matrix_by_field.get(field, {})
        external = dict(evidence_rows.get(field) or {})
        relation = relationship_by_child.get(field)
        support = str(external.get("support_grade") or matrix_row.get("external_support_grade") or "NO_EXTERNAL_EVIDENCE_RECORDED")
        if support != "NO_EXTERNAL_EVIDENCE_RECORDED" and relation and relation["status"] == "DECADE_EMPIRICALLY_CONSISTENT":
            evidence_status = "EXTERNAL_SUPPORT_PLUS_CONSISTENT_RELATIONSHIP"
        elif support != "NO_EXTERNAL_EVIDENCE_RECORDED" and relation and relation["status"] == "DECADE_REVIEW_REQUIRED":
            evidence_status = "EXTERNAL_SUPPORT_BUT_RELATIONSHIP_CONFLICTS"
        elif support != "NO_EXTERNAL_EVIDENCE_RECORDED":
            evidence_status = "EXTERNAL_SUPPORT_PROFILE_REVIEW"
        elif relation and relation["status"] == "DECADE_EMPIRICALLY_CONSISTENT":
            evidence_status = "RELATIONSHIP_SUPPORT_ONLY"
        elif relation and relation["status"] == "DECADE_REVIEW_REQUIRED":
            evidence_status = "RELATIONSHIP_CONFLICTS"
        else:
            evidence_status = "PROFILE_OR_DEFINITION_REVIEW_ONLY"
        candidate_rows.append(
            {
                "source_field": field,
                "post_v3_review_lane": str(matrix_row.get("post_v3_review_lane") or "EVIDENCE_FILE_ONLY"),
                "coverage_shape": str(matrix_row.get("coverage_shape") or ""),
                "external_support_grade": support,
                "external_proposed_label": str(external.get("proposed_label") or matrix_row.get("external_proposed_label") or ""),
                "profile": aggregate_profiles[field],
                "relationship": relation,
                "evidence_status": evidence_status,
                "governance_decision": "UNREVIEWED",
                "governance_note": "Evidence-stack review only. No status automatically promotes a field.",
            }
        )

    status_order = {
        "EXTERNAL_SUPPORT_PLUS_CONSISTENT_RELATIONSHIP": 0,
        "EXTERNAL_SUPPORT_PROFILE_REVIEW": 1,
        "RELATIONSHIP_SUPPORT_ONLY": 2,
        "PROFILE_OR_DEFINITION_REVIEW_ONLY": 3,
        "EXTERNAL_SUPPORT_BUT_RELATIONSHIP_CONFLICTS": 4,
        "RELATIONSHIP_CONFLICTS": 5,
    }
    candidate_rows.sort(
        key=lambda row: (
            status_order.get(str(row["evidence_status"]), 99),
            str(row["source_field"]).casefold(),
        )
    )

    return {
        "schema_version": "1.0.0",
        "scope": "POST_V3_V4_EVIDENCE_STACK_REVIEW",
        "seasons": list(seasons),
        "season_row_counts": season_row_counts,
        "candidate_count": len(candidate_rows),
        "relationship_rule_count": len(relationship_summaries),
        "relationship_status_counts": dict(
            sorted(Counter(str(row["status"]) for row in relationship_summaries).items())
        ),
        "evidence_status_counts": dict(
            sorted(Counter(str(row["evidence_status"]) for row in candidate_rows).items())
        ),
        "relationship_summaries": relationship_summaries,
        "candidates": candidate_rows,
        "interpretation": (
            "This audit combines authoritative semantic evidence, source profiles and empirical subset relationships. "
            "It is a review gate only; promotion remains an explicit human governance decision."
        ),
    }


def write_audit(result: Mapping[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "team_match_v4_evidence_stack.csv"
    json_path = output_dir / "team_match_v4_evidence_stack.json"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = (
            "source_field",
            "post_v3_review_lane",
            "coverage_shape",
            "external_support_grade",
            "external_proposed_label",
            "evidence_status",
            "nonblank_rows",
            "blank_rows",
            "zero_rows",
            "negative_rows",
            "relationship_parent",
            "relationship_rows_compared",
            "relationship_violations",
            "relationship_status",
        )
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result["candidates"]:
            profile = dict(row.get("profile") or {})
            relation = dict(row.get("relationship") or {})
            writer.writerow(
                {
                    "source_field": row.get("source_field", ""),
                    "post_v3_review_lane": row.get("post_v3_review_lane", ""),
                    "coverage_shape": row.get("coverage_shape", ""),
                    "external_support_grade": row.get("external_support_grade", ""),
                    "external_proposed_label": row.get("external_proposed_label", ""),
                    "evidence_status": row.get("evidence_status", ""),
                    "nonblank_rows": profile.get("nonblank_rows", 0),
                    "blank_rows": profile.get("blank_rows", 0),
                    "zero_rows": profile.get("zero_rows", 0),
                    "negative_rows": profile.get("negative_rows", 0),
                    "relationship_parent": relation.get("parent_field", ""),
                    "relationship_rows_compared": relation.get("rows_compared", 0),
                    "relationship_violations": relation.get("violations", 0),
                    "relationship_status": relation.get("status", ""),
                }
            )
    json_path.write_text(json.dumps(dict(result), indent=2, ensure_ascii=False), encoding="utf-8")
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit the post-V3 evidence stack for a larger controlled Team-Match V4 review."
    )
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    matrix_path = args.matrix.expanduser().resolve()
    if not matrix_path.is_file():
        raise SystemExit(
            f"Post-V3 evidence matrix not found: {matrix_path}. Run scripts/build_team_match_post_v3_evidence_matrix.py first."
        )
    result = build_audit(
        _read_csv(matrix_path),
        _read_json(args.evidence.expanduser().resolve()),
    )
    csv_path, json_path = write_audit(result, args.output_dir.expanduser().resolve())
    preview = [
        {
            "source_field": row["source_field"],
            "evidence_status": row["evidence_status"],
            "support": row["external_support_grade"],
            "nonblank_rows": row["profile"]["nonblank_rows"],
            "blank_rows": row["profile"]["blank_rows"],
            "relationship": (
                {
                    "parent": row["relationship"]["parent_field"],
                    "rows_compared": row["relationship"]["rows_compared"],
                    "violations": row["relationship"]["violations"],
                    "status": row["relationship"]["status"],
                }
                if row.get("relationship")
                else None
            ),
        }
        for row in list(result["candidates"])[:30]
    ]
    print(
        json.dumps(
            {
                "candidate_count": result["candidate_count"],
                "relationship_rule_count": result["relationship_rule_count"],
                "relationship_status_counts": result["relationship_status_counts"],
                "evidence_status_counts": result["evidence_status_counts"],
                "relationship_summaries": result["relationship_summaries"],
                "first_30": preview,
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
