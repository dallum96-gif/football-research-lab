from __future__ import annotations

import csv
from pathlib import Path

import club_profile_registry


ROOT = Path(__file__).resolve().parents[1]


def test_registry_covers_every_persistent_club() -> None:
    path = ROOT / "identity" / "team_seasons.csv"

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    expected = {
        str(row["persistent_team_code"]).strip()
        for row in rows
        if str(
            row.get("persistent_team_code") or ""
        ).strip()
    }

    actual = {
        str(profile["persistent_team_code"])
        for profile in club_profile_registry.all_profiles()
    }

    assert actual == expected


def test_arsenal_profile_is_curated() -> None:
    profiles = club_profile_registry.all_profiles()

    arsenal = next(
        profile
        for profile in profiles
        if profile["canonical_name"] == "Arsenal"
    )

    result = club_profile_registry.get_profile(
        arsenal["persistent_team_code"],
        "2025-26",
    )

    assert result is not None
    assert result["status"] == "CURATED"
    assert result["identity"]["founded_year"] == 1886
    assert result["stadium"]["name"] == "Emirates Stadium"
    assert result["leadership"]["manager"]["name"] == "Mikel Arteta"

    honours = {
        item["key"]: item["wins"]
        for item in result["honours"]["categories"]
    }

    assert honours["league"] == 14
    assert honours["fa_cup"] == 14
    assert honours["community_shield"] == 18