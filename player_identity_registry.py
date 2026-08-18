"""Generate the verified FRL FPL-element -> source player identity registry.

The registry is derived from audited exact-name+verified-team matches. A
season-local FPL element may appear under more than one team when a player
moves clubs during a season, so promotion occurs at the (season, element)
level only when all verified evidence resolves to exactly one source playerId.
Records with multiple source identities remain unresolved and are rejected.
"""

from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

import player_identity_crosswalk


OUTPUT = Path("player_identity_registry.csv")
FIELDS = (
    "season",
    "fpl_element",
    "fpl_name_normalized",
    "team_code",
    "source_player_id",
    "match_method",
    "confidence",
    "identity_status",
    "evidence_basis",
)


def build_registry() -> list[dict[str, str]]:
    report = player_identity_crosswalk.summarize()
    if report["review_rows"]:
        raise ValueError(
            f"Cannot promote crosswalk: {report['review_rows']} review rows remain."
        )

    grouped = defaultdict(list)
    for item in report["confirmed"]:
        grouped[(item["season"], item["element"])].append(item)

    rows = []
    unresolved = []

    for key, items in grouped.items():
        source_ids = {item["source_player_id"] for item in items}
        if len(source_ids) != 1:
            unresolved.append((key, sorted(source_ids)))
            continue

        first = items[0]
        teams = sorted({item["team_code"] for item in items if item["team_code"]})
        names = sorted({item["name_norm"] for item in items if item["name_norm"]})
        methods = sorted({item["method"] for item in items if item["method"]})

        rows.append(
            {
                "season": key[0],
                "fpl_element": key[1],
                "fpl_name_normalized": names[0] if names else "",
                "team_code": ";".join(teams),
                "source_player_id": next(iter(source_ids)),
                "match_method": ";".join(methods),
                "confidence": "VERIFIED",
                "identity_status": "VERIFIED",
                "evidence_basis": "exact normalized name + verified seasonal team identity; unique source playerId across all verified team records",
            }
        )

    if unresolved:
        raise ValueError(
            "Cannot promote crosswalk: some seasonal FPL elements resolve to multiple source playerIds. "
            f"Examples: {unresolved[:5]}"
        )

    rows.sort(key=lambda r: (r["season"], int(r["fpl_element"])))
    return rows


def write_registry(output: Path = OUTPUT) -> list[dict[str, str]]:
    rows = build_registry()
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = write_registry()
    print("=" * 88)
    print("FRL VERIFIED PLAYER IDENTITY REGISTRY")
    print("=" * 88)
    print(f"Rows written: {len(rows):,}")
    print(f"Output: {OUTPUT}")
    print("Only deterministic rows with one source playerId are included.")
    print("All unresolved or source-conflicting identities remain outside the registry.")
    print("=" * 88)
