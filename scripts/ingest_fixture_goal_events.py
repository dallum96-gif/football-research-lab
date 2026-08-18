from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_identity_crosswalk
import player_research
import query_lab
from match_stats import fixture_source_match

FIXTURE_FILE = ROOT / "fixtures_master_corrected.csv"
OUTPUT = ROOT / "data" / "fixture_goal_events.csv"
PULSE_BASE = "https://footballapi.pulselive.com/football"
HEADERS = {
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142 Safari/537.36",
    "Accept": "application/json",
}

FIELDS = (
    "season",
    "fixture_id",
    "source_match_id",
    "source_event_id",
    "source_event_type",
    "source_event_seconds",
    "source_event_time_label",
    "source_event_text",
    "source_scorer_name",
    "source_scorer_team",
    "source_scorer_id",
    "identity_status",
    "fpl_element",
    "player_name",
    "side",
    "own_goal",
    "source_url",
    "retrieved_at_utc",
    "goal_count_match",
)


def _norm(value: str | None) -> str:
    return player_identity_crosswalk.normalize_name(value)


def _team_norm(value: str | None) -> str:
    text = (value or "").replace("_", " ").replace("&", " and ")
    return _norm(text)


def _load_fixtures():
    with FIXTURE_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _verified_player_index():
    report = player_identity_crosswalk.summarize()
    if report["review_rows"]:
        raise RuntimeError(
            f"Player identity crosswalk has {report['review_rows']} unresolved review rows."
        )

    names = {}
    for season in player_research.available_seasons():
        for row in player_research._load_season_rows(season):
            element = str(row.get("element") or "").strip()
            if element:
                names[(season, element)] = player_research.display_player_name(row)

    index: dict[tuple[str, str, str], list[tuple[str, str]]] = defaultdict(list)
    for row in report["confirmed"]:
        key = (row["season"], str(row["team_code"]), row["name_norm"])
        element = str(row["element"])
        player_name = names.get((row["season"], element), row["name_norm"])
        index[key].append((element, player_name))

    return {key: tuple(values) for key, values in index.items()}


def _parse_scorer(text: str):
    if not text:
        return None, None
    match = re.search(r"\.\s+(.+?)\s+\(([^)]+)\)", text)
    if not match:
        return None, None
    return match.group(1).strip(), match.group(2).strip()


def _is_goal(event: dict) -> bool:
    event_type = str(event.get("type") or "").strip().casefold()
    return event_type in {"goal", "penalty goal"}


def _request_fixture(source_match_id: str):
    url = f"{PULSE_BASE}/fixtures/{source_match_id}"
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.json(), url


def _score_total(fixture: dict) -> int:
    try:
        return int(fixture["home_score"]) + int(fixture["away_score"])
    except (TypeError, ValueError):
        return 0


def ingest(
    sleep_seconds: float = 0.15,
    limit: int | None = None,
    fixture_key: str | None = None,
):
    fixtures = _load_fixtures()
    identity_rows = query_lab.load_identity_registry()
    player_index = _verified_player_index()

    if fixture_key:
        try:
            target_season, target_fixture_id = fixture_key.split(":", 1)
        except ValueError as exc:
            raise ValueError("--fixture must use SEASON:FIXTURE_ID") from exc
        fixtures = [
            row
            for row in fixtures
            if row["season"] == target_season
            and str(row["fixture_id"]) == target_fixture_id
        ]
        if not fixtures:
            raise ValueError(f"Canonical fixture not found: {fixture_key}")

    if limit is not None:
        fixtures = fixtures[:limit]

    rows: list[dict[str, str]] = []
    retrieved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    for number, fixture in enumerate(fixtures, start=1):
        season = fixture["season"]
        fixture_id = fixture["fixture_id"]
        total_goals = _score_total(fixture)

        if total_goals == 0:
            continue

        resolved = fixture_source_match(fixture, identity_rows)
        if resolved is None:
            print(f"[SKIP] {season}/{fixture_id}: no verified source fixture")
            continue

        source_match_id, source_home, source_away = resolved
        home_source_code = str(source_home.get("team_id") or "").strip()
        away_source_code = str(source_away.get("team_id") or "").strip()
        home_source_team = str(source_home.get("team") or "").strip()
        away_source_team = str(source_away.get("team") or "").strip()

        try:
            payload, source_url = _request_fixture(str(source_match_id))
        except (requests.RequestException, ValueError) as exc:
            print(f"[SKIP] {season}/{fixture_id}: source request failed: {exc}")
            continue

        source_fixture = payload.get("fixture") or {}
        teams = source_fixture.get("teams") or []
        if len(teams) >= 2:
            home_source_team = str((teams[0].get("team") or {}).get("name") or home_source_team).strip()
            away_source_team = str((teams[1].get("team") or {}).get("name") or away_source_team).strip()

        events = ((payload.get("events") or {}).get("content") or [])
        goals = [event for event in events if isinstance(event, dict) and _is_goal(event)]
        goal_count_match = str(len(goals) == total_goals).lower()

        if len(goals) != total_goals:
            print(f"[WARN] {season}/{fixture_id}: score={total_goals}, source goals={len(goals)}")

        for event in goals:
            text = str(event.get("text") or "").strip()
            scorer_name, scorer_team = _parse_scorer(text)
            scorer_team_norm = _team_norm(scorer_team)
            home_match = scorer_team_norm == _team_norm(home_source_team)
            away_match = scorer_team_norm == _team_norm(away_source_team)

            if home_match:
                scorer_side = "home"
                scorer_team_code = home_source_code
            elif away_match:
                scorer_side = "away"
                scorer_team_code = away_source_code
            else:
                scorer_side = ""
                scorer_team_code = ""

            key = (season, scorer_team_code, _norm(scorer_name))
            candidates = player_index.get(key, ()) if scorer_name and scorer_team_code else ()

            identity_status = "VERIFIED" if len(candidates) == 1 else "UNRESOLVED"
            fpl_element = candidates[0][0] if len(candidates) == 1 else ""
            canonical_name = candidates[0][1] if len(candidates) == 1 else ""

            own_goal = "own goal" in text.casefold()
            scoring_side = (
                "away" if scorer_side == "home" else "home" if scorer_side == "away" else ""
            ) if own_goal else scorer_side

            time_block = event.get("time") or {}
            seconds = time_block.get("secs")
            label = str(time_block.get("label") or "").strip()
            player_ids = event.get("playerIds") or []
            source_scorer_id = str(player_ids[0]) if player_ids else ""

            rows.append(
                {
                    "season": season,
                    "fixture_id": fixture_id,
                    "source_match_id": str(source_match_id),
                    "source_event_id": str(event.get("id") or ""),
                    "source_event_type": str(event.get("type") or ""),
                    "source_event_seconds": str(seconds or ""),
                    "source_event_time_label": label,
                    "source_event_text": text,
                    "source_scorer_name": scorer_name or "",
                    "source_scorer_team": scorer_team or "",
                    "source_scorer_id": source_scorer_id,
                    "identity_status": identity_status,
                    "fpl_element": fpl_element,
                    "player_name": canonical_name,
                    "side": scoring_side,
                    "own_goal": str(own_goal).lower(),
                    "source_url": source_url,
                    "retrieved_at_utc": retrieved_at,
                    "goal_count_match": goal_count_match,
                }
            )

        print(f"[{number}/{len(fixtures)}] {season}/{fixture_id}: {len(goals)} goals")
        time.sleep(sleep_seconds)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 88)
    print("FRL FIXTURE GOAL EVENT INGEST")
    print("=" * 88)
    print(f"Fixtures inspected: {len(fixtures):,}")
    print(f"Goal-event rows written: {len(rows):,}")
    print(f"Output: {OUTPUT}")
    print("Only VERIFIED scorer identities are displayed by the GUI.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--fixture", default=None, help="Target canonical fixture as SEASON:FIXTURE_ID")
    parser.add_argument("--sleep", type=float, default=0.15)
    args = parser.parse_args()
    ingest(sleep_seconds=args.sleep, limit=args.limit, fixture_key=args.fixture)
