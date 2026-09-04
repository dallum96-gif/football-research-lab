from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fixture_context_research import (
    FixtureContextUnavailableError,
    fixture_events,
    fixture_tactical_context,
)
from source_field_catalog import SEASONS
from source_family_adapters import season_fixtures

DEFAULT_OUTPUT_DIR = ROOT / "data" / "audits" / "fixture_context_research"


def _identity_status(bridge: object) -> str:
    if not isinstance(bridge, dict):
        return "NO_PLAYER_REFERENCE"
    return str(bridge.get("relationship_status") or bridge.get("status") or "UNKNOWN")


def _fixture_audit(season: str, fixture_id: str) -> dict[str, Any]:
    row: dict[str, Any] = {
        "season": season,
        "fixture_id": str(fixture_id),
        "events_status": "NOT_RUN",
        "event_count": 0,
        "goal_events": 0,
        "card_events": 0,
        "substitution_events": 0,
        "event_primary_verified": 0,
        "event_primary_unresolved": 0,
        "event_secondary_verified": 0,
        "event_secondary_unresolved": 0,
        "tactical_context_status": "NOT_RUN",
        "lineup_player_count": 0,
        "lineup_player_verified": 0,
        "lineup_player_unresolved": 0,
        "formation_sides_available": 0,
        "manager_count": 0,
        "events_error": "",
        "tactical_context_error": "",
    }

    try:
        events = fixture_events(season, str(fixture_id))
        row["events_status"] = "PASS"
        results = list(events.get("results") or [])
        row["event_count"] = len(results)
        types = Counter(str(item.get("type") or "unknown") for item in results)
        row["goal_events"] = types.get("goal", 0)
        row["card_events"] = types.get("card", 0)
        row["substitution_events"] = types.get("substitution", 0)
        for item in results:
            primary = _identity_status(item.get("primary_player_identity"))
            secondary = _identity_status(item.get("secondary_player_identity"))
            if primary == "VERIFIED":
                row["event_primary_verified"] += 1
            elif primary != "NO_PLAYER_REFERENCE":
                row["event_primary_unresolved"] += 1
            if secondary == "VERIFIED":
                row["event_secondary_verified"] += 1
            elif secondary != "NO_PLAYER_REFERENCE":
                row["event_secondary_unresolved"] += 1
    except FixtureContextUnavailableError as exc:
        row["events_status"] = "UNAVAILABLE"
        row["events_error"] = str(exc)
    except Exception as exc:  # audit retains exact unexpected failure
        row["events_status"] = "ERROR"
        row["events_error"] = f"{type(exc).__name__}: {exc}"

    try:
        tactical = fixture_tactical_context(season, str(fixture_id))
        row["tactical_context_status"] = "PASS"
        players = list(tactical.get("players") or [])
        row["lineup_player_count"] = len(players)
        for player in players:
            status = _identity_status(player.get("player_identity"))
            if status == "VERIFIED":
                row["lineup_player_verified"] += 1
            elif status != "NO_PLAYER_REFERENCE":
                row["lineup_player_unresolved"] += 1
        formations = dict(tactical.get("formations") or {})
        row["formation_sides_available"] = sum(
            1
            for value in formations.values()
            if isinstance(value, dict)
            and value.get("status") == "AVAILABLE"
            and value.get("value") not in (None, "")
        )
        managers = tactical.get("managers") or {}
        row["manager_count"] = len(managers.get("items") or []) if isinstance(managers, dict) else 0
    except FixtureContextUnavailableError as exc:
        row["tactical_context_status"] = "UNAVAILABLE"
        row["tactical_context_error"] = str(exc)
    except Exception as exc:  # audit retains exact unexpected failure
        row["tactical_context_status"] = "ERROR"
        row["tactical_context_error"] = f"{type(exc).__name__}: {exc}"

    return row


def build_audit(seasons: Sequence[str] = SEASONS) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    season_fixture_counts: dict[str, int] = {}
    for season in seasons:
        fixtures = tuple(season_fixtures(season))
        season_fixture_counts[season] = len(fixtures)
        for fixture in fixtures:
            fixture_id = str(fixture.get("fixture_id") or "").strip()
            if fixture_id:
                rows.append(_fixture_audit(season, fixture_id))

    event_status_counts = Counter(str(row["events_status"]) for row in rows)
    tactical_status_counts = Counter(str(row["tactical_context_status"]) for row in rows)

    return {
        "schema_version": "1.0.0",
        "seasons": list(seasons),
        "season_fixture_counts": season_fixture_counts,
        "fixture_count": len(rows),
        "event_status_counts": dict(sorted(event_status_counts.items())),
        "tactical_context_status_counts": dict(sorted(tactical_status_counts.items())),
        "total_events": sum(int(row["event_count"]) for row in rows),
        "event_type_counts": {
            "goal": sum(int(row["goal_events"]) for row in rows),
            "card": sum(int(row["card_events"]) for row in rows),
            "substitution": sum(int(row["substitution_events"]) for row in rows),
        },
        "event_identity_counts": {
            "primary_verified": sum(int(row["event_primary_verified"]) for row in rows),
            "primary_unresolved": sum(int(row["event_primary_unresolved"]) for row in rows),
            "secondary_verified": sum(int(row["event_secondary_verified"]) for row in rows),
            "secondary_unresolved": sum(int(row["event_secondary_unresolved"]) for row in rows),
        },
        "lineup_player_rows": sum(int(row["lineup_player_count"]) for row in rows),
        "lineup_identity_counts": {
            "verified": sum(int(row["lineup_player_verified"]) for row in rows),
            "unresolved": sum(int(row["lineup_player_unresolved"]) for row in rows),
        },
        "formation_sides_available": sum(int(row["formation_sides_available"]) for row in rows),
        "manager_rows": sum(int(row["manager_count"]) for row in rows),
        "rows": rows,
        "interpretation": (
            "This audit measures access and identity-bridge coverage for the existing normalised "
            "PulseLive event and lineup evidence seam. It does not promote event semantics, infer "
            "unresolved player identities, or treat source formation/manager fields as canonical."
        ),
    }


OUTPUT_FIELDS = (
    "season",
    "fixture_id",
    "events_status",
    "event_count",
    "goal_events",
    "card_events",
    "substitution_events",
    "event_primary_verified",
    "event_primary_unresolved",
    "event_secondary_verified",
    "event_secondary_unresolved",
    "tactical_context_status",
    "lineup_player_count",
    "lineup_player_verified",
    "lineup_player_unresolved",
    "formation_sides_available",
    "manager_count",
    "events_error",
    "tactical_context_error",
)


def write_audit(result: Mapping[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "fixture_context_research_audit.csv"
    json_path = output_dir / "fixture_context_research_audit.json"

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in result.get("rows") or []:
            writer.writerow({field: row.get(field, "") for field in OUTPUT_FIELDS})

    json_path.write_text(json.dumps(dict(result), indent=2, ensure_ascii=False), encoding="utf-8")
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit generic fixture event/lineup/tactical-context access across preserved seasons."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    result = build_audit()
    csv_path, json_path = write_audit(result, args.output_dir.expanduser().resolve())
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "fixture_count",
                    "season_fixture_counts",
                    "event_status_counts",
                    "tactical_context_status_counts",
                    "total_events",
                    "event_type_counts",
                    "event_identity_counts",
                    "lineup_player_rows",
                    "lineup_identity_counts",
                    "formation_sides_available",
                    "manager_rows",
                )
            }
            | {"csv_output": str(csv_path), "json_output": str(json_path)},
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
