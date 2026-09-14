"""Governed biographical evidence for FRL player profiles.

This module may expose squad metadata only when an explicit FRL player_code
can be joined exactly to squad playerId and the player identity remains
unambiguous. Missing or uncertain identity fails closed.
"""
from __future__ import annotations

from functools import lru_cache
import re
import unicodedata

import player_metadata_source
import player_research


STABLE_FIELDS = (
    "firstName",
    "lastName",
    "displayName",
    "nationality",
    "isoCode",
    "birthDate",
    "birthCountry",
    "preferredFoot",
    "height_cm",
    "weight_kg",
)


def _text(value) -> str:
    return str(value or "").strip()


def _normalise_name(value: str) -> str:
    text = unicodedata.normalize("NFKD", _text(value))
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def _source_name(row: dict) -> str:
    display = _text(row.get("displayName"))
    if display:
        return display

    return " ".join(
        value
        for value in (
            _text(row.get("firstName")),
            _text(row.get("lastName")),
        )
        if value
    )


def _number_or_none(value):
    text = _text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _explicit_player_code(player: dict, requested_code: str) -> str | None:
    requested = _text(requested_code)

    codes = {
        _text(row.get("player_code"))
        for row in player.get("_records", ())
        if _text(row.get("player_code"))
    }

    if len(codes) != 1:
        return None

    code = next(iter(codes))
    return code if code == requested else None


def _candidate_seasons(profile_season: str) -> tuple[str, ...]:
    seasons = [
        season
        for season in player_research.available_seasons()
        if season <= profile_season
    ]
    return tuple(
        sorted(
            seasons,
            key=lambda value: int(value[:4]),
            reverse=True,
        )
    )


@lru_cache(maxsize=512)
def resolve_player_biography(
    profile_season: str,
    player_code: str,
) -> dict:
    player = player_research.player_detail(
        profile_season,
        player_code,
    )

    if player is None:
        return {
            "available": False,
            "identity_status": "UNAVAILABLE",
            "limitations": [
                "Player profile evidence is unavailable."
            ],
        }

    explicit_code = _explicit_player_code(
        player,
        player_code,
    )

    if explicit_code is None:
        return {
            "available": False,
            "identity_status": "WITHHELD",
            "limitations": [
                "Biographical metadata is withheld because this player record does not expose one unambiguous explicit player_code."
            ],
        }

    profile_name = _text(player.get("player_name"))

    for source_season in _candidate_seasons(
        profile_season
    ):
        try:
            rows = (
                player_metadata_source
                .players_by_source_id(source_season)
                .get(explicit_code, ())
            )
        except (FileNotFoundError, ValueError):
            continue

        if not rows:
            continue

        if len(rows) != 1:
            return {
                "available": False,
                "identity_status": "WITHHELD",
                "limitations": [
                    f"Biographical metadata is withheld because squad playerId {explicit_code} is duplicated in {source_season}."
                ],
            }

        row = rows[0]
        source_name = _source_name(row)

        if (
            not source_name
            or _normalise_name(source_name)
            != _normalise_name(profile_name)
        ):
            # Exact ID alone is not enough for this first governed version.
            # Continue looking backwards rather than promoting uncertain evidence.
            continue

        current_season = (
            source_season == profile_season
        )

        return {
            "available": True,
            "identity_status": "VERIFIED",
            "first_name": _text(row.get("firstName")) or None,
            "last_name": _text(row.get("lastName")) or None,
            "display_name": source_name or None,
            "nationality": _text(row.get("nationality")) or None,
            "nationality_code": _text(row.get("isoCode")) or None,
            "birth_date": _text(row.get("birthDate")) or None,
            "birth_country": _text(row.get("birthCountry")) or None,
            "preferred_foot": _text(row.get("preferredFoot")) or None,
            "height_cm": _number_or_none(row.get("height_cm")),
            "weight_kg": _number_or_none(row.get("weight_kg")),

            # These are season-sensitive. Never silently copy them
            # from an older squad snapshot.
            "shirt_number": (
                _text(row.get("shirtNumber")) or None
                if current_season
                else None
            ),
            "join_date": (
                _text(row.get("joinDate")) or None
                if current_season
                else None
            ),
            "on_loan": (
                _text(row.get("onLoan")) or None
                if current_season
                else None
            ),

            "evidence": {
                "identity_rule": (
                    "exact explicit FRL player_code == squad playerId "
                    "plus exact normalised player-name agreement"
                ),
                "player_code": explicit_code,
                "profile_season": profile_season,
                "source_season": source_season,
                "historical_fallback": not current_season,
                "source_file": _text(row.get("_source_file")),
            },
            "limitations": (
                [
                    f"Stable biographical fields use the newest verified prior squad snapshot ({source_season}) because no matching {profile_season} squad record is available.",
                    "Season-sensitive squad attributes are not backfilled from an earlier season.",
                ]
                if not current_season
                else []
            ),
        }

    return {
        "available": False,
        "identity_status": "WITHHELD",
        "limitations": [
            "No squad metadata row satisfied the governed exact-ID and exact-name identity rule."
        ],
    }
