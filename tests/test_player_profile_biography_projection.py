from __future__ import annotations

import csv

import player_profile_biography_projection


FIELDS = [
    "season",
    "source_player_id",
    "team_name",
    "display_name",
    "first_name",
    "last_name",
    "nationality",
    "nationality_code",
    "birth_date",
    "birth_country",
    "preferred_foot",
    "height_cm",
    "weight_kg",
    "shirt_number",
    "join_date",
    "on_loan",
    "source_file",
]


def _write(path, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_biography_runtime_uses_packaged_source_only(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "bio.csv"
    _write(packaged, [{
        "season": "2026-27",
        "source_player_id": "184029",
        "team_name": "Arsenal",
        "display_name": "Martin Ødegaard",
        "first_name": "Martin",
        "last_name": "Ødegaard",
        "nationality": "Norway",
        "nationality_code": "NO",
        "birth_date": "1998-12-17",
        "birth_country": "Norway",
        "preferred_foot": "Left",
        "height_cm": "178",
        "weight_kg": "68",
        "shirt_number": "8",
        "join_date": "2021-08-20",
        "on_loan": "False",
        "source_file": "Arsenal_3/squad/2026-27_squad.csv",
    }])
    monkeypatch.setattr(player_profile_biography_projection, "PACKAGED", packaged)
    player_profile_biography_projection.clear_caches()
    try:
        result = player_profile_biography_projection.resolve_biography(
            "2026-27", "184029", "Martin Ødegaard", "Arsenal"
        )
        assert result["available"] is True
        assert result["shirt_number"] == "8"
        assert result["preferred_foot"] == "Left"
        assert result["evidence"]["runtime_source"] == "data/player_profile_biography_v1.csv"
    finally:
        player_profile_biography_projection.clear_caches()


def test_historical_fallback_does_not_backfill_season_sensitive_fields(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "bio.csv"
    _write(packaged, [{
        "season": "2025-26",
        "source_player_id": "184029",
        "team_name": "Arsenal",
        "display_name": "Martin Ødegaard",
        "first_name": "Martin",
        "last_name": "Ødegaard",
        "nationality": "Norway",
        "nationality_code": "NO",
        "birth_date": "1998-12-17",
        "birth_country": "Norway",
        "preferred_foot": "Left",
        "height_cm": "178",
        "weight_kg": "68",
        "shirt_number": "8",
        "join_date": "2021-08-20",
        "on_loan": "False",
        "source_file": "Arsenal_3/squad/2025-26_squad.csv",
    }])
    monkeypatch.setattr(player_profile_biography_projection, "PACKAGED", packaged)
    player_profile_biography_projection.clear_caches()
    try:
        result = player_profile_biography_projection.resolve_biography(
            "2026-27", "184029", "Martin Ødegaard", "Arsenal"
        )
        assert result["available"] is True
        assert result["evidence"]["historical_fallback"] is True
        assert result["shirt_number"] is None
        assert result["join_date"] is None
    finally:
        player_profile_biography_projection.clear_caches()
