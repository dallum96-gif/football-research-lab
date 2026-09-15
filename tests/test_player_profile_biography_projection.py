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


def _odegaard_row(season="2026-27") -> dict:
    return {
        "season": season,
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
        "source_file": f"Arsenal_3/squad/{season}_squad.csv",
    }


def test_biography_runtime_uses_packaged_source_only(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "bio.csv"
    _write(packaged, [_odegaard_row()])
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
        assert result["evidence"]["identity_rule"] == "VERIFIED_PROFILE_SOURCE_PLAYER_ID"
        assert result["evidence"]["exact_normalised_name_corroboration"] is True
    finally:
        player_profile_biography_projection.clear_caches()


def test_verified_source_id_survives_legitimate_display_name_variant(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "bio.csv"
    row = _odegaard_row()
    row.update({
        "source_player_id": "226597",
        "display_name": "Gabriel Magalhães",
        "first_name": "Gabriel",
        "last_name": "dos Santos Magalhães",
        "nationality": "Brazil",
        "nationality_code": "BR",
        "birth_date": "1997-12-19",
        "birth_country": "Brazil",
        "preferred_foot": "Left",
        "height_cm": "190",
        "weight_kg": "92",
        "shirt_number": "6",
        "join_date": "2020-09-01",
    })
    _write(packaged, [row])
    monkeypatch.setattr(player_profile_biography_projection, "PACKAGED", packaged)
    player_profile_biography_projection.clear_caches()
    try:
        result = player_profile_biography_projection.resolve_biography(
            "2026-27", "226597", "Gabriel dos Santos Magalhães", "Arsenal"
        )
        assert result["available"] is True
        assert result["shirt_number"] == "6"
        assert result["nationality"] == "Brazil"
        assert result["evidence"]["exact_normalised_name_corroboration"] is False
        assert any("display names differ" in limitation for limitation in result["limitations"])
    finally:
        player_profile_biography_projection.clear_caches()


def test_historical_fallback_does_not_backfill_season_sensitive_fields(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "bio.csv"
    _write(packaged, [_odegaard_row("2025-26")])
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


def test_conflicting_stable_facts_for_same_verified_source_id_fail_closed(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "bio.csv"
    first = _odegaard_row()
    second = _odegaard_row()
    second["team_name"] = "Other Club"
    second["birth_date"] = "1999-12-17"
    _write(packaged, [first, second])
    monkeypatch.setattr(player_profile_biography_projection, "PACKAGED", packaged)
    player_profile_biography_projection.clear_caches()
    try:
        result = player_profile_biography_projection.resolve_biography(
            "2026-27", "184029", "Martin Ødegaard", "Arsenal"
        )
        assert result["available"] is False
        assert result["identity_status"] == "WITHHELD"
    finally:
        player_profile_biography_projection.clear_caches()
