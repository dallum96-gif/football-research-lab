"""Season-aware club context for Player Profile.

Team membership is a relationship, not a property of player identity.  This
module therefore derives profile club context from the selected season's
player-fixture records instead of treating the alphabetically sorted club list
as a current club.
"""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache

import query_lab


def _text(value: object) -> str:
    return str(value or "").strip()


def _parse_kickoff(value: object) -> datetime | None:
    text = _text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@lru_cache(maxsize=20)
def _fixture_indexes(season: str) -> tuple[dict[str, datetime], dict[str, datetime]]:
    rows, _columns = query_lab.load_csv(query_lab.FIXTURE_FILE)
    by_id: dict[str, datetime] = {}
    by_code: dict[str, datetime] = {}
    for row in rows:
        if _text(row.get("season")) != season:
            continue
        kickoff = _parse_kickoff(row.get("kickoff_time"))
        if kickoff is None:
            continue
        fixture_id = _text(row.get("fixture_id"))
        fixture_code = _text(row.get("fixture_code"))
        if fixture_id:
            by_id[fixture_id] = kickoff
        if fixture_code:
            by_code[fixture_code] = kickoff
    return by_id, by_code


def _row_kickoff(season: str, row: dict) -> datetime | None:
    by_id, by_code = _fixture_indexes(season)
    for key in ("fixture", "fixture_id"):
        value = _text(row.get(key))
        if value and value in by_id:
            return by_id[value]
    value = _text(row.get("fixture_code"))
    if value and value in by_code:
        return by_code[value]
    return None


def resolve_club_context(player: dict, season: str) -> dict:
    clubs = {
        _text(row.get("_club"))
        for row in player.get("_records", ())
        if _text(row.get("_club"))
    }
    if not clubs:
        clubs = {_text(value) for value in player.get("clubs", ()) if _text(value)}

    ordered = sorted(clubs, key=str.casefold)
    if not ordered:
        return {
            "primary_club": None,
            "clubs": [],
            "status": "UNAVAILABLE",
            "evidence": {},
            "limitations": ["No season club relationship is available."],
        }

    if len(ordered) == 1:
        return {
            "primary_club": ordered[0],
            "clubs": ordered,
            "status": "VERIFIED_SINGLE_CLUB",
            "evidence": {"club_count": 1},
            "limitations": [],
        }

    observations: list[tuple[datetime, str]] = []
    for row in player.get("_records", ()):
        club = _text(row.get("_club"))
        kickoff = _row_kickoff(season, row)
        if club and kickoff is not None:
            observations.append((kickoff, club))

    if observations:
        observations.sort(key=lambda item: item[0])
        latest_time = observations[-1][0]
        latest_clubs = {club for moment, club in observations if moment == latest_time}
        if len(latest_clubs) == 1:
            primary = next(iter(latest_clubs))
            remaining = [club for club in ordered if club != primary]
            return {
                "primary_club": primary,
                "clubs": [primary, *remaining],
                "status": "VERIFIED_LATEST_FIXTURE",
                "evidence": {
                    "club_count": len(ordered),
                    "latest_observed_kickoff": latest_time.isoformat(),
                },
                "limitations": [
                    "Multiple clubs are recorded in the selected season; primary club is the club in the latest canonical fixture observation."
                ],
            }

    return {
        "primary_club": None,
        "clubs": ordered,
        "status": "MULTI_CLUB_UNRESOLVED_PRIMARY",
        "evidence": {"club_count": len(ordered)},
        "limitations": [
            "Multiple clubs are recorded in the selected season and no unique latest canonical fixture observation resolves a primary club."
        ],
    }


__all__ = ["resolve_club_context"]
