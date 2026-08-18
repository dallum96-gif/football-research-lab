from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import player_identity_crosswalk
import player_research
import query_lab
from match_stats import fixture_source_match

RAW = ROOT / "data" / "raw" / "fixture_goal_events_pulselive.csv"
OUT = ROOT / "data" / "fixture_goal_events.csv"

FIELDS = (
    "season",
    "fixture_id",
    "source_match_id",
    "source_pulse_fixture_id",
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


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Source file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verified_player_index():
    report = player_identity_crosswalk.summarize()
    if report["review_rows"]:
        raise RuntimeError(
            f"Player identity crosswalk has {report['review_rows']} unresolved review rows; "
            "refusing to promote goal events to canonical data."
        )

    names: dict[tuple[str, str], str] = {}
    for season in player_research.available_seasons():
        for row in player_research._load_season_rows(season):
            element = str(row.get("element") or "").strip()
            if element:
                names[(season, element)] = player_research.display_player_name(row)

    index: dict[tuple[str, str], list[tuple[str, str, str]]] = defaultdict(list)
    for row in report["confirmed"]:
        season = str(row["season"]).strip()
        source_id = str(row["source_player_id"]).strip()
        element = str(row["element"]).strip()
        team_code = str(row.get("team_code") or "").split(";")[0].strip()
        if source_id and element:
            index[(season, source_id)].append(
                (element, names.get((season, element), row.get("name_norm", "")), team_code)
            )
    return {key: tuple(values) for key, values in index.items()}


def main() -> None:
    raw = load_rows(RAW)
    identity_rows = query_lab.load_identity_registry()
    player_index = verified_player_index()

    fixtures = {
        (row["season"], str(row["fixture_id"])): row
        for row in query_lab.load_csv(query_lab.FIXTURE_FILE)[0]
    }

    canonical_rows: list[dict[str, str]] = []
    skipped = 0

    for row in raw:
        season = str(row.get("season") or "").strip()
        source_match_id = str(row.get("source_match_id") or "").strip()
        if not season or not source_match_id:
            skipped += 1
            continue

        # Reconstruct the canonical fixture through the existing FRL mechanism.
        candidates = []
        for fixture in fixtures.values():
            if fixture["season"] != season:
                continue
            resolved = fixture_source_match(fixture, identity_rows)
            if resolved and str(resolved[0]) == source_match_id:
                candidates.append((fixture, resolved))

        if len(candidates) != 1:
            raise RuntimeError(
                f"Expected exactly one canonical fixture for source match "
                f"{season}/{source_match_id}; found {len(candidates)}"
            )

        fixture, (resolved_source_id, source_home, source_away) = candidates[0]
        if str(resolved_source_id) != source_match_id:
            raise RuntimeError("Source-match reconciliation changed the source identifier")

        source_player_id = str(row.get("source_scorer_id") or "").strip()
        matches = player_index.get((season, source_player_id), ())
        if len(matches) != 1:
            raise RuntimeError(
                f"Refusing canonical promotion for {season}/{source_match_id}: "
                f"source player {source_player_id!r} has {len(matches)} verified identity matches"
            )

        element, player_name, team_code = matches[0]
        home_team_code = str(source_home.get("team_id") or "").strip()
        away_team_code = str(source_away.get("team_id") or "").strip()

        scorer_side = "home" if team_code == home_team_code else "away" if team_code == away_team_code else ""
        if not scorer_side:
            raise RuntimeError(
                f"Verified player {source_player_id} cannot be reconciled to either "
                f"source team for {season}/{fixture['fixture_id']}"
            )

        own_goal = str(row.get("own_goal") or "false").casefold() == "true"
        scoring_side = "away" if scorer_side == "home" else "home" if own_goal else scorer_side
        if not own_goal:
            scoring_side = scorer_side

        canonical_rows.append(
            {
                **row,
                "fixture_id": str(fixture["fixture_id"]),
                "identity_status": "VERIFIED",
                "fpl_element": element,
                "player_name": player_name,
                "side": scoring_side,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(canonical_rows)

    print("=" * 88)
    print("FRL GOAL EVENT VALIDATION")
    print("=" * 88)
    print(f"Raw rows inspected:        {len(raw):,}")
    print(f"Canonical rows written:    {len(canonical_rows):,}")
    print(f"Rows skipped:              {skipped:,}")
    print(f"Output:                    {OUT}")
    print(f"Validated at:              {datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}")
    print("Canonical promotion requires verified fixture and player identity.")


if __name__ == "__main__":
    main()
