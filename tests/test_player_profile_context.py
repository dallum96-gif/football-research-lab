from __future__ import annotations

import csv

import player_profile_context


def _write_fixture_file(path, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["season", "fixture_id", "fixture_code", "kickoff_time"],
        )
        writer.writeheader()
        writer.writerows(rows)


def test_single_club_context_is_unambiguous() -> None:
    result = player_profile_context.resolve_club_context(
        {"_records": [{"_club": "Arsenal"}, {"_club": "Arsenal"}]},
        "2026-27",
    )
    assert result["primary_club"] == "Arsenal"
    assert result["status"] == "VERIFIED_SINGLE_CLUB"


def test_multi_club_context_uses_latest_canonical_fixture(monkeypatch, tmp_path) -> None:
    fixture_file = tmp_path / "fixtures.csv"
    _write_fixture_file(
        fixture_file,
        [
            {
                "season": "2025-26",
                "fixture_id": "100",
                "fixture_code": "",
                "kickoff_time": "2025-08-01T15:00:00+00:00",
            },
            {
                "season": "2025-26",
                "fixture_id": "200",
                "fixture_code": "",
                "kickoff_time": "2026-01-10T15:00:00+00:00",
            },
        ],
    )
    monkeypatch.setattr(player_profile_context.query_lab, "FIXTURE_FILE", str(fixture_file))
    player_profile_context._fixture_indexes.cache_clear()
    try:
        result = player_profile_context.resolve_club_context(
            {
                "_records": [
                    {"_club": "Old Club", "fixture": "100"},
                    {"_club": "New Club", "fixture": "200"},
                ]
            },
            "2025-26",
        )
        assert result["primary_club"] == "New Club"
        assert result["clubs"] == ["New Club", "Old Club"]
        assert result["status"] == "VERIFIED_LATEST_FIXTURE"
    finally:
        player_profile_context._fixture_indexes.cache_clear()


def test_multi_club_context_with_no_temporal_evidence_withholds_primary() -> None:
    result = player_profile_context.resolve_club_context(
        {
            "_records": [
                {"_club": "Alpha Club"},
                {"_club": "Beta Club"},
            ]
        },
        "2025-26",
    )
    assert result["primary_club"] is None
    assert result["status"] == "MULTI_CLUB_UNRESOLVED_PRIMARY"
