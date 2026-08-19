from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_lab
from ingest_fixture_goal_events import HEADERS, PULSE_BASE, _pulse_fixture_id, _request_fixture, _load_fixtures

REPORT = ROOT / "data" / "raw" / "fixture_goal_events_stage_report.csv"


def read_report() -> list[dict[str, str]]:
    with REPORT.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def is_goal_like(event: dict) -> bool:
    text = str(event.get("text") or "").casefold()
    event_type = str(event.get("type") or "").casefold()
    return (
        event_type in {"goal", "penalty goal", "own goal"}
        or "goal!" in text
        or "scores!" in text
        or "own goal" in text
        or "penalty" in text and "goal" in text
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose PulseLive goal-event staging failures without modifying project data.")
    parser.add_argument("--season", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    report = [r for r in read_report() if r.get("status") in {"GOAL_COUNT_MISMATCH", "REQUEST_FAILED"}]
    if args.season:
        report = [r for r in report if r.get("season") == args.season]
    if args.limit is not None:
        report = report[:args.limit]

    fixtures = {(r.get("season", ""), str(r.get("fixture_id", ""))): r for r in _load_fixtures()}
    identity_rows = query_lab.load_identity_registry()

    print("=" * 88)
    print("FRL PULSELIVE GOAL-EVENT MISMATCH DIAGNOSTIC")
    print("READ-ONLY")
    print("=" * 88)
    print(f"Cases in scope: {len(report)}")

    aggregate_types = Counter()
    suspicious = []

    for n, row in enumerate(report, start=1):
        season = row.get("season", "")
        fixture_id = str(row.get("canonical_fixture_id", "")).strip()
        source_match_id = str(row.get("source_match_id", "")).strip()
        expected = row.get("expected_goal_count", "")
        print(f"\n[{n}/{len(report)}] {season}/{fixture_id} source={source_match_id} expected={expected} status={row.get('status')}")

        fixture = fixtures.get((season, fixture_id))
        if fixture is None:
            print("  [BLOCK] canonical fixture row not found")
            continue

        try:
            pulse_fixture_id = _pulse_fixture_id(season, source_match_id)
            print(f"  PulseLive fixture ID: {pulse_fixture_id}")
        except Exception as exc:
            print(f"  [BLOCK] PulseLive fixture index failed: {exc}")
            continue

        if not pulse_fixture_id:
            print("  [BLOCK] no PulseLive fixture ID")
            continue

        try:
            response = requests.get(
                f"{PULSE_BASE}/fixtures/{pulse_fixture_id}/textstream/EN",
                params={"pageSize": 1000, "sort": "desc"},
                headers=HEADERS,
                timeout=20,
            )
            print(f"  HTTP: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', '')}")
            print(f"  Body length: {len(response.content):,}")
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            print(f"  [REQUEST/DECODE ERROR] {type(exc).__name__}: {exc}")
            continue

        events = ((payload.get("events") or {}).get("content") or [])
        print(f"  Total source events: {len(events)}")

        types = Counter(str(e.get("type") or "").strip().casefold() for e in events if isinstance(e, dict))
        aggregate_types.update(types)
        print(f"  Event types: {dict(types)}")

        goals = [e for e in events if isinstance(e, dict) and str(e.get("type") or "").strip().casefold() in {"goal", "penalty goal", "own goal"}]
        goal_like = [e for e in events if isinstance(e, dict) and is_goal_like(e)]
        print(f"  Explicit goal-type events: {len(goals)}")
        print(f"  Goal-like events by text/type: {len(goal_like)}")

        for event in goal_like:
            item = {
                "id": event.get("id"),
                "type": event.get("type"),
                "time": (event.get("time") or {}).get("label"),
                "text": str(event.get("text") or "").strip(),
                "playerIds": event.get("playerIds") or [],
            }
            suspicious.append((season, fixture_id, item))
            print("  GOAL-LIKE:", json.dumps(item, ensure_ascii=False))

    print("\n" + "=" * 88)
    print("AGGREGATE NON-GOAL-TYPE COVERAGE")
    print("=" * 88)
    print(dict(aggregate_types))
    print(f"Goal-like events inspected: {len(suspicious)}")
    print("No files modified.")


if __name__ == "__main__":
    main()
