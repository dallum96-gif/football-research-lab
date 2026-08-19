from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import query_lab
from ingest_fixture_goal_events import (
    _load_fixtures,
    _pulse_fixture_id,
    _request_fixture,
    _score_total,
    _is_goal,
    _parse_scorer,
)
from match_stats import fixture_source_match

STAGED_RAW = ROOT / "data" / "raw" / "fixture_goal_events_pulselive.staged.csv"
STAGE_REPORT = ROOT / "data" / "raw" / "fixture_goal_events_stage_report.csv"

RAW_FIELDS = (
    "season", "canonical_fixture_id", "source_match_id", "source_pulse_fixture_id",
    "expected_goal_count", "observed_goal_count", "goal_count_match",
    "source_event_id", "source_event_type", "source_event_seconds",
    "source_event_time_label", "source_event_text", "source_scorer_name",
    "source_scorer_team", "source_scorer_id", "source_assist_ids",
    "source_fixture_home", "source_fixture_away", "source_fixture_home_score",
    "source_fixture_away_score", "source_url", "retrieved_at_utc",
)

REPORT_FIELDS = (
    "season", "canonical_fixture_id", "source_match_id", "source_pulse_fixture_id",
    "expected_goal_count", "observed_goal_count", "status", "error",
    "retrieved_at_utc",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if rows:
        missing = sorted(set(fields) - set(rows[0]))
        if missing:
            raise RuntimeError(f"Stage schema mismatch in {path}: missing {missing}")
    return rows


def atomic_csv(path: Path, rows: list[dict[str, str]], fields: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
    tmp.replace(path)


def fixture_scope(season: str | None, limit: int | None) -> list[dict[str, str]]:
    fixtures = _load_fixtures()
    if season:
        fixtures = [r for r in fixtures if r.get("season", "").strip() == season]
    if limit is not None:
        fixtures = fixtures[:limit]
    return fixtures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage PulseLive goal evidence for canonical FRL fixtures without touching canonical output."
    )
    parser.add_argument("--season", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.20)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    identity_rows = query_lab.load_identity_registry()
    fixtures = fixture_scope(args.season, args.limit)
    staged_raw = read_csv(STAGED_RAW, RAW_FIELDS)
    reports = read_csv(STAGE_REPORT, REPORT_FIELDS)

    completed = {
        (r["season"], r["canonical_fixture_id"])
        for r in reports
        if r.get("status") in {"OK", "NO_GOALS_EXPECTED"}
    }

    raw_index = {
        (r["season"], r["source_match_id"], r["source_event_id"]): r
        for r in staged_raw
    }
    report_index = {(r["season"], r["canonical_fixture_id"]): r for r in reports}

    print("=" * 88, flush=True)
    print("FRL PULSELIVE GOAL-EVENT STAGING", flush=True)
    print("CANONICAL OUTPUT PROTECTED", flush=True)
    print("=" * 88, flush=True)
    print(f"Canonical fixtures in scope: {len(fixtures):,}", flush=True)
    print(f"Previously staged fixtures:  {len(completed):,}", flush=True)

    for number, fixture in enumerate(fixtures, start=1):
        season = str(fixture.get("season") or "").strip()
        fixture_id = str(fixture.get("fixture_id") or "").strip()
        if not season or not fixture_id:
            raise RuntimeError(f"Canonical fixture has blank identity at row {number}")

        key = (season, fixture_id)
        if args.resume and key in completed:
            continue

        expected = _score_total(fixture)
        stamp = now_utc()

        if expected == 0:
            report_index[key] = {
                "season": season,
                "canonical_fixture_id": fixture_id,
                "source_match_id": "",
                "source_pulse_fixture_id": "",
                "expected_goal_count": "0",
                "observed_goal_count": "0",
                "status": "NO_GOALS_EXPECTED",
                "error": "",
                "retrieved_at_utc": stamp,
            }
            print(f"[{number}/{len(fixtures)}] {season}/{fixture_id}: 0 goals expected", flush=True)
            atomic_csv(STAGE_REPORT, list(report_index.values()), REPORT_FIELDS)
            continue

        resolved = fixture_source_match(fixture, identity_rows)
        if not resolved:
            report_index[key] = {
                "season": season,
                "canonical_fixture_id": fixture_id,
                "source_match_id": "",
                "source_pulse_fixture_id": "",
                "expected_goal_count": str(expected),
                "observed_goal_count": "",
                "status": "SOURCE_MATCH_UNRESOLVED",
                "error": "Existing FRL fixture_source_match() did not resolve a unique source match",
                "retrieved_at_utc": stamp,
            }
            print(f"[BLOCK] {number}/{len(fixtures)} {season}/{fixture_id}: source-match unresolved", flush=True)
            atomic_csv(STAGE_REPORT, list(report_index.values()), REPORT_FIELDS)
            continue

        source_match_id, source_home, source_away = resolved
        source_match_id = str(source_match_id).strip()
        pulse_fixture_id = _pulse_fixture_id(season, source_match_id)
        if not pulse_fixture_id:
            report_index[key] = {
                "season": season,
                "canonical_fixture_id": fixture_id,
                "source_match_id": source_match_id,
                "source_pulse_fixture_id": "",
                "expected_goal_count": str(expected),
                "observed_goal_count": "",
                "status": "PULSELIVE_ID_UNRESOLVED",
                "error": "No PulseLive fixture identity for verified source match",
                "retrieved_at_utc": stamp,
            }
            print(f"[BLOCK] {number}/{len(fixtures)} {season}/{fixture_id}: no PulseLive identity", flush=True)
            atomic_csv(STAGE_REPORT, list(report_index.values()), REPORT_FIELDS)
            continue

        payload = None
        source_url = ""
        last_error = ""
        for attempt in range(args.retries + 1):
            try:
                payload, source_url = _request_fixture(pulse_fixture_id)
                break
            except Exception as exc:  # staging records the failure; promotion later remains fail-closed
                last_error = repr(exc)
                if attempt < args.retries:
                    time.sleep(max(args.sleep, 0.5) * (attempt + 1))

        if payload is None:
            report_index[key] = {
                "season": season,
                "canonical_fixture_id": fixture_id,
                "source_match_id": source_match_id,
                "source_pulse_fixture_id": pulse_fixture_id,
                "expected_goal_count": str(expected),
                "observed_goal_count": "",
                "status": "REQUEST_FAILED",
                "error": last_error,
                "retrieved_at_utc": now_utc(),
            }
            print(f"[BLOCK] {number}/{len(fixtures)} {season}/{fixture_id}: request failed", flush=True)
            atomic_csv(STAGE_REPORT, list(report_index.values()), REPORT_FIELDS)
            continue

        events = ((payload.get("events") or {}).get("content") or [])
        goals = [event for event in events if isinstance(event, dict) and _is_goal(event)]
        observed = len(goals)
        stamp = now_utc()

        for event in goals:
            event_id = str(event.get("id") or "").strip()
            if not event_id:
                raise RuntimeError(f"Goal event missing source event id: {season}/{fixture_id}")

            text = str(event.get("text") or "").strip()
            scorer_name, scorer_team = _parse_scorer(text)
            player_ids = [str(x).strip() for x in (event.get("playerIds") or []) if str(x).strip()]
            scorer_id = player_ids[0] if player_ids else ""
            assist_ids = ";".join(player_ids[1:])
            time_block = event.get("time") or {}

            raw_index[(season, source_match_id, event_id)] = {
                "season": season,
                "canonical_fixture_id": fixture_id,
                "source_match_id": source_match_id,
                "source_pulse_fixture_id": pulse_fixture_id,
                "expected_goal_count": str(expected),
                "observed_goal_count": str(observed),
                "goal_count_match": str(observed == expected).lower(),
                "source_event_id": event_id,
                "source_event_type": str(event.get("type") or ""),
                "source_event_seconds": str(time_block.get("secs") or ""),
                "source_event_time_label": str(time_block.get("label") or "").strip(),
                "source_event_text": text,
                "source_scorer_name": scorer_name or "",
                "source_scorer_team": scorer_team or "",
                "source_scorer_id": scorer_id,
                "source_assist_ids": assist_ids,
                "source_fixture_home": str(source_home.get("name") or "").strip(),
                "source_fixture_away": str(source_away.get("name") or "").strip(),
                "source_fixture_home_score": str(fixture.get("home_score") or ""),
                "source_fixture_away_score": str(fixture.get("away_score") or ""),
                "source_url": source_url,
                "retrieved_at_utc": stamp,
            }

        status = "OK" if observed == expected else "GOAL_COUNT_MISMATCH"
        report_index[key] = {
            "season": season,
            "canonical_fixture_id": fixture_id,
            "source_match_id": source_match_id,
            "source_pulse_fixture_id": pulse_fixture_id,
            "expected_goal_count": str(expected),
            "observed_goal_count": str(observed),
            "status": status,
            "error": "" if status == "OK" else f"Expected {expected} goals, observed {observed}",
            "retrieved_at_utc": stamp,
        }

        staged_raw = list(raw_index.values())
        atomic_csv(STAGED_RAW, staged_raw, RAW_FIELDS)
        atomic_csv(STAGE_REPORT, list(report_index.values()), REPORT_FIELDS)
        print(
            f"[{number}/{len(fixtures)}] {season}/{fixture_id}: "
            f"source={source_match_id}, expected={expected}, observed={observed}, status={status}",
            flush=True,
        )
        time.sleep(args.sleep)

    print("=" * 88, flush=True)
    print(f"STAGED GOAL ROWS: {len(raw_index):,}", flush=True)
    print(f"FIXTURE REPORT ROWS: {len(report_index):,}", flush=True)
    print(f"RAW STAGE: {STAGED_RAW}", flush=True)
    print(f"REPORT:    {STAGE_REPORT}", flush=True)
    print("CANONICAL fixture_goal_events.csv: UNTOUCHED", flush=True)
    print("Next step is the fail-closed proof validation/promotion stage.", flush=True)


if __name__ == "__main__":
    main()
