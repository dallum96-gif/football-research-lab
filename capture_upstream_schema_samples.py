"""Capture a local raw upstream schema sample set for FRL discovery.

This tool is deliberately additive and local-first. It preserves raw JSON payloads
before the master variable enumerator inspects them. It does not write canonical
FRL data or change identity relationships.

Sources captured:
- public FPL bootstrap-static and fixtures;
- selected FPL live-gameweek payloads;
- selected current/legacy player summaries from bootstrap player IDs;
- selected Premier League/PulseLive match evidence through the existing
  ``pulselive_live.snapshot`` adapter.

The goal is schema discovery, not exhaustive historical extraction. Once the raw
sample set exists locally, ``enumerate_master_variable_universe.py --json-root``
can enumerate nested fields without repeatedly requesting upstream services.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DEFAULT_ROOT = ROOT / "raw_upstream"
FPL_BASE = "https://fantasy.premierleague.com/api"
USER_AGENT = "Mozilla/5.0"


def fetch_json(url: str, timeout: int = 20) -> object:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"request failed: {url}: {exc}") from exc


def write_json(root: Path, relative_path: str, payload: object) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_sample_match_ids(limit: int) -> list[str]:
    path = ROOT / "data" / "fixture_match_stats.csv"
    if not path.is_file():
        return []
    ids: list[str] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            value = str(row.get("source_match_id") or "").strip()
            if value and value not in seen:
                seen.add(value)
                ids.append(value)
            if len(ids) >= limit:
                break
    return ids


def capture_fpl(root: Path, live_gameweeks: int, player_samples: int) -> int:
    count = 0
    bootstrap = fetch_json(f"{FPL_BASE}/bootstrap-static/")
    write_json(root, "fpl/bootstrap-static.json", bootstrap)
    count += 1

    fixtures = fetch_json(f"{FPL_BASE}/fixtures/")
    write_json(root, "fpl/fixtures.json", fixtures)
    count += 1

    if isinstance(bootstrap, dict):
        events = bootstrap.get("events") or []
        elements = bootstrap.get("elements") or []

        event_ids = [int(e["id"]) for e in events if isinstance(e, dict) and e.get("id") is not None]
        selected_events = event_ids[:live_gameweeks]
        if len(event_ids) > live_gameweeks:
            selected_events.append(event_ids[-1])
        for event_id in dict.fromkeys(selected_events):
            try:
                payload = fetch_json(f"{FPL_BASE}/event/{event_id}/live/")
            except RuntimeError as exc:
                print(f"WARN FPL live {event_id}: {exc}", file=sys.stderr)
                continue
            write_json(root, f"fpl/event-live/event-{event_id}.json", payload)
            count += 1

        # One player from each FPL position where possible gives us a better
        # schema sample than taking four arbitrary rows.
        chosen: list[dict] = []
        seen_types: set[object] = set()
        for element in elements:
            if not isinstance(element, dict) or element.get("id") is None:
                continue
            element_type = element.get("element_type")
            if element_type not in seen_types:
                chosen.append(element)
                seen_types.add(element_type)
            if len(chosen) >= player_samples:
                break
        for element in chosen:
            element_id = int(element["id"])
            try:
                payload = fetch_json(f"{FPL_BASE}/element-summary/{element_id}/")
            except RuntimeError as exc:
                print(f"WARN FPL element-summary {element_id}: {exc}", file=sys.stderr)
                continue
            write_json(root, f"fpl/element-summary/element-{element_id}.json", payload)
            count += 1

    return count


def capture_pulselive(root: Path, match_samples: int) -> int:
    try:
        from pulselive_live import snapshot
    except ImportError as exc:
        raise RuntimeError("Could not import pulselive_live.py from the repository root") from exc

    match_ids = read_sample_match_ids(match_samples)
    count = 0
    for match_id in match_ids:
        try:
            payload = snapshot(match_id)
        except Exception as exc:
            print(f"WARN PulseLive match {match_id}: {exc}", file=sys.stderr)
            continue
        write_json(root, f"pulselive/match-{match_id}/snapshot.json", payload)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--live-gameweeks", type=int, default=3)
    parser.add_argument("--player-samples", type=int, default=4)
    parser.add_argument("--match-samples", type=int, default=5)
    args = parser.parse_args()

    args.root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "tool": Path(__file__).name,
        "sources": {
            "fpl": "https://fantasy.premierleague.com/api",
            "pulselive": "existing repository pulselive_live.py adapter",
        },
        "note": "Raw schema samples only; not canonical FRL data.",
    }
    write_json(args.root, "capture_manifest.json", manifest)

    fpl_count = capture_fpl(args.root, max(0, args.live_gameweeks), max(1, args.player_samples))
    pl_count = capture_pulselive(args.root, max(0, args.match_samples))

    print("FRL UPSTREAM SCHEMA SAMPLE CAPTURE")
    print("=" * 80)
    print(f"FPL payloads captured: {fpl_count}")
    print(f"PulseLive snapshots captured: {pl_count}")
    print(f"Raw archive: {args.root}")
    print("")
    print("Next step:")
    print("python .\\enumerate_master_variable_universe.py --json-root .\\raw_upstream")


if __name__ == "__main__":
    main()
