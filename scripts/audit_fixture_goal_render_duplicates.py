from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOALS = ROOT / "data" / "fixture_goal_events.csv"


def load_rows():
    if not GOALS.is_file():
        raise FileNotFoundError(GOALS)
    with GOALS.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def clean(value: object) -> str:
    return str(value or "").replace("_", " ").strip()


def main() -> None:
    rows = [r for r in load_rows() if clean(r.get("identity_status")) == "VERIFIED"]

    by_fixture: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_fixture[(clean(row.get("season")), clean(row.get("fixture_id")))].append(row)

    duplicate_event_ids = []
    duplicate_goal_signatures = []
    duplicated_fixture_payloads = []

    for key, fixture_rows in sorted(by_fixture.items()):
        event_ids = [clean(r.get("source_event_id")) for r in fixture_rows]
        id_counts = Counter(x for x in event_ids if x)
        repeated_ids = {x: n for x, n in id_counts.items() if n > 1}
        if repeated_ids:
            duplicate_event_ids.append((key, repeated_ids))

        signatures = Counter(
            (
                clean(r.get("source_event_time_label")),
                clean(r.get("source_scorer_name")),
                clean(r.get("source_scorer_team")),
                clean(r.get("source_fixture_home")),
                clean(r.get("source_fixture_away")),
            )
            for r in fixture_rows
        )
        repeated_signatures = {sig: n for sig, n in signatures.items() if n > 1}
        if repeated_signatures:
            duplicate_goal_signatures.append((key, repeated_signatures))

        payload_counts = Counter(
            (
                clean(r.get("source_event_id")),
                clean(r.get("source_event_seconds")),
                clean(r.get("source_event_time_label")),
                clean(r.get("source_scorer_name")),
                clean(r.get("source_scorer_team")),
            )
            for r in fixture_rows
        )
        repeated_payloads = {payload: n for payload, n in payload_counts.items() if n > 1}
        if repeated_payloads:
            duplicated_fixture_payloads.append((key, repeated_payloads))

    print("============================================================")
    print("FIXTURE GOAL RENDER DUPLICATE AUDIT")
    print("============================================================")
    print(f"Canonical verified rows: {len(rows)}")
    print(f"Fixtures with evidence: {len(by_fixture)}")
    print()
    print("=== DUPLICATE EVENT IDs ===")
    print(f"Fixtures affected: {len(duplicate_event_ids)}")
    for key, repeats in duplicate_event_ids[:50]:
        print(f"{key}: {repeats}")
    print()
    print("=== DUPLICATE GOAL SIGNATURES ===")
    print(f"Fixtures affected: {len(duplicate_goal_signatures)}")
    for key, repeats in duplicate_goal_signatures[:50]:
        print(f"{key}:")
        for signature, count in repeats.items():
            print(f"  {count}x {signature}")
    print()
    print("=== DUPLICATE EVENT PAYLOADS ===")
    print(f"Fixtures affected: {len(duplicated_fixture_payloads)}")
    for key, repeats in duplicated_fixture_payloads[:50]:
        print(f"{key}:")
        for payload, count in repeats.items():
            print(f"  {count}x {payload}")
    print()
    if duplicate_event_ids or duplicate_goal_signatures or duplicated_fixture_payloads:
        print("AUDIT: DUPLICATES FOUND")
    else:
        print("AUDIT: NO DUPLICATE EVENTS IN CANONICAL EVIDENCE")


if __name__ == "__main__":
    main()
