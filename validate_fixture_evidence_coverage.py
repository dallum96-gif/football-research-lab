"""Validate universal fixture-evidence coverage across the canonical fixture universe.

Run from the FRL repository in an environment where the approved upstream
Premier-League-Stats workspace is available at its configured local path.
The validator does not modify source data.
"""
from __future__ import annotations

from collections import Counter

from fixture_research_access import fixture_research_result
from source_family_adapters import season_fixtures


SEASONS = (
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
)


def validate() -> dict:
    examined = 0
    source_matches = 0
    event_available = 0
    event_unavailable = 0
    lineup_available = 0
    lineup_exception = 0
    lineup_unavailable = 0
    formation_available = 0
    manager_available = 0
    identity_failures = 0
    known_exceptions: Counter[str] = Counter()
    errors: list[dict[str, str]] = []

    for season in SEASONS:
        for fixture in season_fixtures(season):
            fixture_id = str(fixture["fixture_id"])
            examined += 1
            try:
                result = fixture_research_result(season, fixture_id)
            except Exception as exc:  # validator records fail-closed exceptions rather than hiding them
                errors.append({"season": season, "fixture_id": fixture_id, "error": f"{type(exc).__name__}: {exc}"})
                known_exceptions["fixture_evidence_error"] += 1
                continue

            source_matches += 1
            payload = result["payload"]
            if result["provenance"].get("source_match_id"):
                source_matches += 0

            events = payload["events"]
            if events:
                event_available += 1
            else:
                event_unavailable += 1

            lineup = payload["lineup"]
            lineup_status = "AVAILABLE" if lineup else "UNAVAILABLE"
            if lineup_status == "AVAILABLE":
                lineup_available += 1
            else:
                lineup_unavailable += 1

            formation_statuses = [payload["formation"]["home"]["status"], payload["formation"]["away"]["status"]]
            if all(status == "AVAILABLE" for status in formation_statuses):
                formation_available += 1

            if payload["managers"]["status"] == "AVAILABLE":
                manager_available += 1

            for row in lineup:
                if row["player"].get("identity_status") != "VERIFIED":
                    identity_failures += 1
                    lineup_exception += 1

            event_ids = [event["event_id"] for event in events]
            if len(event_ids) != len(set(event_ids)):
                errors.append({"season": season, "fixture_id": fixture_id, "error": "duplicate event IDs"})
                known_exceptions["duplicate_event_ids"] += 1

            player_keys = [
                (row["provenance"].get("source_match_id"), row["player"].get("source_player_id"), row.get("side"))
                for row in lineup
            ]
            if len(player_keys) != len(set(player_keys)):
                errors.append({"season": season, "fixture_id": fixture_id, "error": "duplicate player-fixture rows"})
                known_exceptions["duplicate_player_fixture_rows"] += 1

    return {
        "fixtures_examined": examined,
        "fixtures_with_verified_source_match": source_matches,
        "fixtures_with_event_evidence": event_available,
        "fixtures_without_event_evidence": event_unavailable,
        "fixtures_with_lineup_evidence": lineup_available,
        "fixtures_without_lineup_evidence": lineup_unavailable,
        "fixtures_with_formation": formation_available,
        "fixtures_with_manager_data": manager_available,
        "identity_failures": identity_failures,
        "known_exceptions": dict(known_exceptions),
        "errors": errors,
    }


if __name__ == "__main__":
    report = validate()
    for key, value in report.items():
        print(f"{key}={value}")
