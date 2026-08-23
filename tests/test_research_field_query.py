from __future__ import annotations

import research_field_query as rq


def test_field_catalog_exposes_uncatalogued_fields():
    original = rq.available_fields
    rq.available_fields = lambda family, season: ("customMetric",)
    try:
        rows = rq.field_catalog("team_match", "2025-26")
        row = next(item for item in rows if item["source_field"] == "customMetric")
        assert row["registry_status"] == "UNCATALOGUED"
        assert row["present_in_season"] is True
    finally:
        rq.available_fields = original


def test_fixture_field_values_preserve_source_identity(monkeypatch):
    monkeypatch.setattr(rq, "available_fields", lambda family, season: ("customMetric",))
    monkeypatch.setattr(
        rq,
        "team_match_source_rows",
        lambda season, fixture_id: (
            {"team_id": "home", "matchId": "m1", "customMetric": "12"},
            {"team_id": "away", "matchId": "m1", "customMetric": "8"},
        ),
    )

    result = rq.fixture_field_values("2025-26", "101", "customMetric")
    assert result["source_rows"] == 2
    assert result["results"][0]["source_match_id"] == "m1"
    assert result["results"][0]["source_team_id"] == "home"


def test_unknown_field_fails_closed(monkeypatch):
    monkeypatch.setattr(rq, "available_fields", lambda family, season: ("known",))
    try:
        rq.player_season_field_values("2025-26", "unknown")
    except ValueError as exc:
        assert "unavailable" in str(exc)
    else:
        raise AssertionError("Unknown source field should fail closed")


def test_temporal_note_is_visible():
    monkeypatch = None
    # The query result contract explicitly refuses to infer availability time.
    assert "historical availability" in rq._result("team_match", "2025-26", "known", [])["temporal_note"]
