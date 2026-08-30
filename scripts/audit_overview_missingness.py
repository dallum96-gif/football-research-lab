from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_source_routes import SEASONS, direct_index, num


SHOT_TOTAL = "totalScoringAtt"
SHOT_COMPONENTS = (
    "ontargetScoringAtt",
    "shotOffTarget",
    "blockedScoringAtt",
)
SHOT_FIELDS = (SHOT_TOTAL, *SHOT_COMPONENTS)
EPSILON = 1e-9


def all_team_rows(matches: dict) -> tuple[tuple[str, str, dict], ...]:
    rows = []
    for match_id, sides in matches.items():
        for side in ("home", "away"):
            row = sides.get(side)
            if row is not None:
                rows.append((match_id, side, row))
    return tuple(rows)


def shot_identity_value(row: dict, target: str) -> float | None:
    values = {field: num(row.get(field)) for field in SHOT_FIELDS}
    others = [field for field in SHOT_FIELDS if field != target]
    if any(values[field] is None for field in others):
        return None
    if target == SHOT_TOTAL:
        return sum(values[field] for field in SHOT_COMPONENTS)
    return values[SHOT_TOTAL] - sum(
        values[field]
        for field in SHOT_COMPONENTS
        if field != target
    )


def season_audit(root: Path, season: str) -> dict:
    matches, _, fields = direct_index(root, season)
    rows = all_team_rows(matches)

    fully_observed = 0
    identity_exact = 0
    identity_mismatches = []
    for match_id, side, row in rows:
        values = {field: num(row.get(field)) for field in SHOT_FIELDS}
        if any(value is None for value in values.values()):
            continue
        fully_observed += 1
        expected = sum(values[field] for field in SHOT_COMPONENTS)
        difference = values[SHOT_TOTAL] - expected
        if abs(difference) <= EPSILON:
            identity_exact += 1
        elif len(identity_mismatches) < 10:
            identity_mismatches.append(
                {
                    "match_id": match_id,
                    "venue": side,
                    "team_id": str(row.get("team_id", "")),
                    "team": row.get("team"),
                    "total": values[SHOT_TOTAL],
                    "components_sum": expected,
                    "difference": difference,
                }
            )

    blank_inference = {}
    for target in SHOT_FIELDS:
        blanks = inferable = zero = positive = negative = explicit_zero = 0
        max_abs_nonzero = 0.0
        examples = []
        for match_id, side, row in rows:
            observed_value = num(row.get(target))
            if observed_value is not None:
                if abs(observed_value) <= EPSILON:
                    explicit_zero += 1
                continue
            if target not in fields:
                continue

            blanks += 1
            inferred = shot_identity_value(row, target)
            if inferred is None:
                continue
            inferable += 1
            if abs(inferred) <= EPSILON:
                zero += 1
                continue
            if inferred > EPSILON:
                positive += 1
            else:
                negative += 1
            max_abs_nonzero = max(max_abs_nonzero, abs(inferred))
            if len(examples) < 10:
                examples.append(
                    {
                        "match_id": match_id,
                        "venue": side,
                        "team_id": str(row.get("team_id", "")),
                        "team": row.get("team"),
                        "inferred_value": inferred,
                    }
                )

        blank_inference[target] = {
            "blank_team_sides": blanks,
            "explicit_numeric_zero_team_sides": explicit_zero,
            "inferable_from_other_shot_fields": inferable,
            "inferred_zero": zero,
            "inferred_positive": positive,
            "inferred_negative": negative,
            "max_abs_nonzero": max_abs_nonzero,
            "nonzero_examples": examples,
        }

    possession_missing = []
    for match_id, side, row in rows:
        if "possessionPercentage" in fields and num(row.get("possessionPercentage")) is None:
            possession_missing.append(
                {
                    "match_id": match_id,
                    "venue": side,
                    "team_id": str(row.get("team_id", "")),
                    "team": row.get("team"),
                    "opponent": row.get("opponent"),
                    "kickoff": row.get("kickoff"),
                }
            )

    return {
        "team_sides": len(rows),
        "shot_identity": {
            "fully_observed_team_sides": fully_observed,
            "identity_exact_team_sides": identity_exact,
            "identity_exact_rate": identity_exact / fully_observed if fully_observed else None,
            "mismatch_examples": identity_mismatches,
        },
        "blank_inference": blank_inference,
        "possession_missing": possession_missing,
    }


def field_diagnostic(*, inferable: int, zero: int, positive: int, negative: int) -> str:
    if not inferable:
        return "REVIEW_REQUIRED"
    if zero == inferable:
        return "BLANK_ZERO_STRONGLY_SUPPORTED_BY_SHOT_IDENTITY"

    zero_rate = zero / inferable
    if zero_rate >= 0.99 and positive == 0 and negative > 0:
        return "SPARSE_ZERO_STRONGLY_SUPPORTED_WITH_SOURCE_ANOMALIES"
    return "REVIEW_REQUIRED"


def summary(seasons: dict) -> dict:
    fully_observed = sum(
        seasons[season]["shot_identity"]["fully_observed_team_sides"]
        for season in SEASONS
    )
    exact = sum(
        seasons[season]["shot_identity"]["identity_exact_team_sides"]
        for season in SEASONS
    )

    fields = {}
    for target in SHOT_FIELDS:
        blanks = sum(
            seasons[season]["blank_inference"][target]["blank_team_sides"]
            for season in SEASONS
        )
        explicit_zero = sum(
            seasons[season]["blank_inference"][target]["explicit_numeric_zero_team_sides"]
            for season in SEASONS
        )
        inferable = sum(
            seasons[season]["blank_inference"][target]["inferable_from_other_shot_fields"]
            for season in SEASONS
        )
        zero = sum(
            seasons[season]["blank_inference"][target]["inferred_zero"]
            for season in SEASONS
        )
        positive = sum(
            seasons[season]["blank_inference"][target]["inferred_positive"]
            for season in SEASONS
        )
        negative = sum(
            seasons[season]["blank_inference"][target]["inferred_negative"]
            for season in SEASONS
        )
        fields[target] = {
            "blank_team_sides": blanks,
            "explicit_numeric_zero_team_sides": explicit_zero,
            "inferable_from_other_shot_fields": inferable,
            "inferred_zero": zero,
            "inferred_positive": positive,
            "inferred_negative": negative,
            "zero_rate_when_inferable": zero / inferable if inferable else None,
            "diagnostic": field_diagnostic(
                inferable=inferable,
                zero=zero,
                positive=positive,
                negative=negative,
            ),
            "production_rule_approved": False,
        }

    possession_missing = [
        {"season": season, **item}
        for season in SEASONS
        for item in seasons[season]["possession_missing"]
    ]

    return {
        "shot_identity": {
            "fully_observed_team_sides": fully_observed,
            "identity_exact_team_sides": exact,
            "identity_exact_rate": exact / fully_observed if fully_observed else None,
            "by_season": {
                season: seasons[season]["shot_identity"]
                for season in SEASONS
            },
        },
        "shot_fields": fields,
        "possession_missing_team_sides": len(possession_missing),
        "possession_missing": possession_missing,
    }


def markdown(report: dict) -> str:
    identity = report["summary"]["shot_identity"]
    lines = [
        "# FRL Team Stats Overview missingness audit",
        "",
        "Diagnostic evidence only. This audit does not directly change production missingness semantics.",
        "",
        "## Shot identity",
        "",
        "The tested historical identity is:",
        "",
        "`totalScoringAtt = ontargetScoringAtt + shotOffTarget + blockedScoringAtt`",
        "",
        f"Fully observed team-sides: **{identity['fully_observed_team_sides']}**  ",
        f"Exact identity matches: **{identity['identity_exact_team_sides']}**  ",
        f"Exact rate: **{identity['identity_exact_rate']:.4%}**",
        "",
        "The identity is exact on every fully observed row from 2016-17 through 2024-25. The audit preserves 2025-26 exceptions as source anomalies rather than forcing the historical partition onto them.",
        "",
        "## Blank shot-field inference",
        "",
        "Negative inferred values are treated as evidence that the source row violates the partition identity, not as evidence that the missing count is negative.",
        "",
        "| Field | Blank sides | Explicit zero | Inferable | Inferred zero | Positive | Negative/anomaly | Zero rate | Diagnostic |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for field, item in report["summary"]["shot_fields"].items():
        rate = item["zero_rate_when_inferable"]
        rate_text = "" if rate is None else f"{rate:.2%}"
        lines.append(
            f"| `{field}` | {item['blank_team_sides']} | {item['explicit_numeric_zero_team_sides']} | "
            f"{item['inferable_from_other_shot_fields']} | {item['inferred_zero']} | "
            f"{item['inferred_positive']} | {item['inferred_negative']} | {rate_text} | "
            f"`{item['diagnostic']}` |"
        )

    lines += ["", "## Possession gaps", ""]
    missing = report["summary"]["possession_missing"]
    if not missing:
        lines.append("No raw possession gaps found.")
    else:
        lines.append("| Season | Match ID | Venue | Team | Opponent | Kickoff |")
        lines.append("|---|---|---|---|---|---|")
        for item in missing:
            lines.append(
                f"| {item['season']} | `{item['match_id']}` | {item['venue']} | "
                f"{item.get('team') or ''} | {item.get('opponent') or ''} | {item.get('kickoff') or ''} |"
            )

    lines += [
        "",
        "## Interpretation",
        "",
        "A field can be labelled as strongly supporting sparse-zero encoding when a large set of blank observations is independently resolved to zero by the validated shot identity and there are no inferred positive missing values. Isolated negative residuals are preserved as source-row anomalies. Production adoption still requires an explicit governed field-level missingness rule.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit Team Stats Overview missingness using internal source invariants."
    )
    parser.add_argument("--pl-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, default=Path("overview_missingness.json"))
    parser.add_argument("--md-out", type=Path, default=Path("overview_missingness.md"))
    args = parser.parse_args()

    if not args.pl_root.is_dir():
        raise SystemExit(f"PL source root not found: {args.pl_root}")

    seasons = {season: season_audit(args.pl_root, season) for season in SEASONS}
    report = {
        "schema_version": "1.1.0",
        "scope": "2016-17_to_2025-26",
        "live_api_calls": False,
        "seasons": seasons,
        "summary": summary(seasons),
        "warning": "Diagnostic evidence only; production missingness semantics remain governed separately.",
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.md_out.write_text(markdown(report), encoding="utf-8")

    identity = report["summary"]["shot_identity"]
    print("FRL TEAM STATS OVERVIEW MISSINGNESS AUDIT")
    print(
        "shot identity: "
        f"{identity['identity_exact_team_sides']}/{identity['fully_observed_team_sides']} "
        f"({identity['identity_exact_rate']:.4%})"
    )
    for field, item in report["summary"]["shot_fields"].items():
        print(
            f"{field}: blanks={item['blank_team_sides']} inferable={item['inferable_from_other_shot_fields']} "
            f"zero={item['inferred_zero']} positive={item['inferred_positive']} "
            f"negative={item['inferred_negative']} {item['diagnostic']}"
        )
    print(f"possession missing team-sides: {report['summary']['possession_missing_team_sides']}")
    print(f"JSON: {args.json_out}")
    print(f"Markdown: {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
