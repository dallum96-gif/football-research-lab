"""Runtime-only packaged biography projection for Player Profile.

Raw squad folders are build-time evidence.  Runtime profile requests read only
this tracked projection, resolved through the governed Player Profile identity
seam.  Missing or ambiguous evidence fails closed.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGED = ROOT / "data" / "player_profile_biography_v1.csv"

STABLE_FIELDS = (
    "first_name",
    "last_name",
    "display_name",
    "nationality",
    "nationality_code",
    "birth_date",
    "birth_country",
    "preferred_foot",
    "height_cm",
    "weight_kg",
)


def _text(value: object) -> str:
    return str(value or "").strip()


def _normalise(value: object) -> str:
    text = unicodedata.normalize("NFKD", _text(value))
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def _number(value: object) -> float | None:
    text = _text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


@lru_cache(maxsize=1)
def _rows() -> tuple[dict[str, str], ...]:
    if not PACKAGED.is_file():
        return tuple()
    with PACKAGED.open("r", encoding="utf-8-sig", newline="") as handle:
        return tuple(dict(row) for row in csv.DictReader(handle))


def _season_key(value: str) -> int:
    try:
        return int(value[:4])
    except (TypeError, ValueError):
        return -1


def _stable_payload(row: dict[str, str]) -> dict:
    return {
        "first_name": _text(row.get("first_name")) or None,
        "last_name": _text(row.get("last_name")) or None,
        "display_name": _text(row.get("display_name")) or None,
        "nationality": _text(row.get("nationality")) or None,
        "nationality_code": _text(row.get("nationality_code")) or None,
        "birth_date": _text(row.get("birth_date")) or None,
        "birth_country": _text(row.get("birth_country")) or None,
        "preferred_foot": _text(row.get("preferred_foot")) or None,
        "height_cm": _number(row.get("height_cm")),
        "weight_kg": _number(row.get("weight_kg")),
    }


@lru_cache(maxsize=1024)
def resolve_biography(
    profile_season: str,
    source_player_id: str,
    profile_name: str,
    primary_club: str | None,
) -> dict:
    source_player_id = _text(source_player_id)
    if not source_player_id:
        return {
            "available": False,
            "identity_status": "UNRESOLVED",
            "limitations": ["No verified Player-Season/portrait identity is available for biography lookup."],
        }

    candidates = [
        row
        for row in _rows()
        if _text(row.get("source_player_id")) == source_player_id
        and _season_key(_text(row.get("season"))) <= _season_key(profile_season)
    ]
    if not candidates:
        return {
            "available": False,
            "identity_status": "UNAVAILABLE",
            "limitations": ["No packaged squad biography row exists for the verified source player identity."],
        }

    seasons = sorted({_text(row.get("season")) for row in candidates}, key=_season_key, reverse=True)
    for source_season in seasons:
        season_rows = [row for row in candidates if _text(row.get("season")) == source_season]
        name_rows = [
            row
            for row in season_rows
            if _normalise(row.get("display_name")) == _normalise(profile_name)
        ]
        if not name_rows:
            continue

        stable_payloads = {
            tuple((field, _text(row.get(field))) for field in STABLE_FIELDS)
            for row in name_rows
        }
        if len(stable_payloads) != 1:
            return {
                "available": False,
                "identity_status": "WITHHELD",
                "limitations": ["Packaged biography rows disagree on stable biographical fields."],
            }

        selected = name_rows[0]
        current = source_season == profile_season
        sensitive_row: dict[str, str] | None = None
        if current:
            if len(name_rows) == 1:
                sensitive_row = name_rows[0]
            elif primary_club:
                club_matches = [
                    row for row in name_rows
                    if _normalise(row.get("team_name")) == _normalise(primary_club)
                ]
                if len(club_matches) == 1:
                    sensitive_row = club_matches[0]

        return {
            "available": True,
            "identity_status": "VERIFIED",
            **_stable_payload(selected),
            "shirt_number": _text(sensitive_row.get("shirt_number")) or None if sensitive_row else None,
            "join_date": _text(sensitive_row.get("join_date")) or None if sensitive_row else None,
            "on_loan": _text(sensitive_row.get("on_loan")) or None if sensitive_row else None,
            "evidence": {
                "profile_season": profile_season,
                "source_season": source_season,
                "source_player_id": source_player_id,
                "historical_fallback": not current,
                "runtime_source": "data/player_profile_biography_v1.csv",
            },
            "limitations": (
                [
                    f"Stable biographical fields use the newest verified prior packaged squad snapshot ({source_season}).",
                    "Season-sensitive squad attributes are not backfilled from an earlier season.",
                ]
                if not current
                else (
                    ["Season-sensitive squad attributes are withheld because multiple current-season club rows remain unresolved."]
                    if sensitive_row is None and len(name_rows) > 1
                    else []
                )
            ),
        }

    return {
        "available": False,
        "identity_status": "WITHHELD",
        "limitations": ["No packaged biography row satisfies the verified source-id plus exact-normalised-name rule."],
    }


def clear_caches() -> None:
    _rows.cache_clear()
    resolve_biography.cache_clear()


__all__ = ["PACKAGED", "clear_caches", "resolve_biography"]
