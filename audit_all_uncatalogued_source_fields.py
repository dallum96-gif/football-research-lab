"""Audit all currently uncatalogued FRL source fields.

This is a conservative review aid. It does not promote fields automatically.
It partitions every uncatalogued field into:
- likely_safe_review: name/coverage suggests a direct source-native metric,
  but still requires source-level semantic confirmation before promotion;
- needs_semantic_review: ambiguous, composite, contextual, outcome-sensitive,
  or otherwise unsafe to infer from the field name alone;
- structural_or_metadata: fields that describe state/context rather than a
  research metric and should be assessed under the appropriate source contract.

The script is intentionally fail-closed: no result is a promotion decision.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from source_field_review_queue import build_queue


@dataclass(frozen=True)
class ReviewRow:
    family: str
    source_field: str
    coverage_class: str
    disposition: str
    reason: str


COMPOSITE_TERMS = {
    "and",
    "excl",
    "including",
    "inc",
    "attempt",
    "attempted",
    "second",
    "intentional",
    "deadball",
    "setplay",
    "openplay",
    "outsidebox",
    "insidebox",
    "oppositionhalf",
    "ownhalf",
}

STRUCTURAL_TERMS = {
    "id",
    "code",
    "name",
    "team",
    "venue",
    "position",
    "gameweek",
    "kickoff",
    "season",
    "date",
    "time",
    "height",
    "weight",
    "age",
    "country",
    "nationality",
}

RESEARCH_TERMS = {
    "goal", "assist", "shot", "cross", "pass", "tackle", "duel", "aerial",
    "dribble", "touch", "clearance", "interception", "foul", "save", "block",
    "chance", "progression", "carry", "rating", "expected", "offside", "card",
}


def _tokens(name: str) -> set[str]:
    # camelCase + common underscore/dash patterns
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    spaced = spaced.replace("_", " ").replace("-", " ").lower()
    return {t for t in spaced.split() if t}


def _row_value(row, key: str):
    """Read either the historical dict queue rows or an object-like row."""
    if isinstance(row, dict):
        return row[key]
    return getattr(row, key)


def classify(row) -> ReviewRow:
    field = _row_value(row, "source_field")
    family = _row_value(row, "family")
    coverage_class = _row_value(row, "coverage_class")
    tokens = _tokens(field)

    if tokens & STRUCTURAL_TERMS and not (tokens & RESEARCH_TERMS):
        return ReviewRow(
            family, field, coverage_class,
            "STRUCTURAL_OR_METADATA",
            "field appears to describe identity/context/metadata rather than a research metric",
        )

    if len(tokens & COMPOSITE_TERMS) >= 1 or any(x in field.lower() for x in ("attempt", "excl", "including", "second")):
        return ReviewRow(
            family, field, coverage_class,
            "NEEDS_SEMANTIC_REVIEW",
            "composite/contextual naming; source definition should be verified rather than inferred",
        )

    if tokens & RESEARCH_TERMS:
        return ReviewRow(
            family, field, coverage_class,
            "LIKELY_DIRECT_METRIC",
            "research-relevant source-native metric name; still requires source-level semantic confirmation",
        )

    return ReviewRow(
        family, field, coverage_class,
        "NEEDS_SEMANTIC_REVIEW",
        "field semantics cannot be established safely from name/coverage alone",
    )


def run() -> list[ReviewRow]:
    queue = build_queue()
    return [classify(row) for row in queue]


def print_report(rows: list[ReviewRow]) -> None:
    print("=" * 120)
    print("FRL FULL UNCATALOGUED SOURCE-FIELD REVIEW AUDIT")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 120)
    print(f"Fields reviewed: {len(rows)}")

    counts = {}
    for row in rows:
        counts[row.disposition] = counts.get(row.disposition, 0) + 1

    for key in ("LIKELY_DIRECT_METRIC", "NEEDS_SEMANTIC_REVIEW", "STRUCTURAL_OR_METADATA"):
        print(f"  {key:24} {counts.get(key, 0)}")

    for disposition in ("LIKELY_DIRECT_METRIC", "NEEDS_SEMANTIC_REVIEW", "STRUCTURAL_OR_METADATA"):
        subset = [r for r in rows if r.disposition == disposition]
        print("\n" + disposition)
        print("-" * 120)
        for row in subset:
            print(f"{row.family:14} | {row.source_field:45} | {row.coverage_class:14} | {row.reason}")

    print("\nIMPORTANT")
    print("- This audit reviews every uncatalogued field.")
    print("- No field is promoted automatically.")
    print("- Promotion requires source-level semantic evidence and registry/test updates.")
    print("- Unknown or ambiguous fields remain fail-closed.")
    print("=" * 120)


if __name__ == "__main__":
    print_report(run())
