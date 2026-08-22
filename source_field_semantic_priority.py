"""Read-only prioritisation of uncatalogued source fields for semantic review.

This module does not promote fields or assert semantics. It only ranks the existing
review queue using conservative, explainable signals: decade coverage, source family,
and name-based research relevance. Human/contract review remains required.
"""
from __future__ import annotations

from source_field_review_queue import build_review_queue

HIGH_VALUE_TERMS = (
    "expected",
    "progressive",
    "accurate",
    "totalpass",
    "accuratepass",
    "cross",
    "tackle",
    "interception",
    "dribble",
    "carry",
    "duel",
    "aerial",
    "keypass",
    "chance",
    "shot",
    "touch",
    "assist",
    "goal",
    "save",
    "clearance",
    "block",
    "foul",
)

LOW_PRIORITY_TERMS = (
    "code",
    "id",
    "name",
    "team",
    "player",
    "venue",
    "match",
    "ground",
    "attendance",
)

NEGATIVE_PREFIXES = ("un", "in")


def _score(row: dict) -> tuple[int, list[str]]:
    field = row["source_field"].casefold()
    family = row["family"]
    coverage = row["coverage_class"]
    seasons_present = int(row["seasons_present"])

    score = 0
    reasons: list[str] = []

    if coverage == "CORE_DECADE":
        score += 40
        reasons.append("core-decade coverage")
    elif coverage == "LONG_RUN":
        score += 25
        reasons.append("long-run coverage")
    elif coverage == "INTERMITTENT":
        score += 10
        reasons.append("intermittent coverage")
    else:
        score += 2
        reasons.append("single-season coverage")

    if family in {"player_match", "player_season"}:
        score += 15
        reasons.append("player research family")
    elif family == "team_match":
        score += 10
        reasons.append("team research family")

    matched_high = []
    for term in HIGH_VALUE_TERMS:
        if term not in field:
            continue
        if term in {"successful"} and any(field.startswith(prefix + term) for prefix in NEGATIVE_PREFIXES):
            continue
        if term == "successful" and f"unsuccessful" in field:
            continue
        matched_high.append(term)

    if matched_high:
        score += min(30, 6 * len(matched_high))
        reasons.append("research-relevant name: " + ", ".join(matched_high[:4]))

    matched_low = [
        term for term in LOW_PRIORITY_TERMS
        if field == term or field.endswith(term)
    ]
    if matched_low:
        score -= 10
        reasons.append("identity/metadata-style name")

    if "unsuccessful" in field:
        reasons.append("negative outcome/reverse-polarity term")

    score += min(seasons_present, 10)
    return score, reasons


def build_priority_queue(limit: int | None = None) -> list[dict]:
    queue = []
    for row in build_review_queue():
        score, reasons = _score(row)
        item = dict(row)
        item["review_priority_score"] = score
        item["priority_reasons"] = tuple(reasons)
        queue.append(item)

    queue.sort(
        key=lambda row: (-row["review_priority_score"], row["family"], row["source_field"])
    )
    return queue if limit is None else queue[:limit]


def print_report(rows: list[dict], limit: int = 50) -> None:
    print("=" * 120)
    print("FRL SOURCE-FIELD SEMANTIC REVIEW PRIORITY")
    print("READ ONLY - NO FILES WILL BE WRITTEN")
    print("=" * 120)
    print(f"Uncatalogued fields ranked: {len(rows)}")
    print(f"Showing top: {min(limit, len(rows))}")
    print()
    print("rank  score  family         source_field                              coverage       reason")
    print("-" * 120)
    for rank, row in enumerate(rows[:limit], start=1):
        reasons = "; ".join(row["priority_reasons"])
        print(
            f"{rank:>4}  {row['review_priority_score']:>5}  "
            f"{row['family']:<14} {row['source_field']:<40} "
            f"{row['coverage_class']:<13} {reasons}"
        )
    print()
    print("Priority is a review aid only; no semantic or canonical promotion is implied.")
    print("=" * 120)


if __name__ == "__main__":
    print_report(build_priority_queue())
