from __future__ import annotations

import fixture_research_access as access


def _source_evidence(*, source_player_id: str = "501", source_formation_order=None):
    return {
        "status": "AVAILABLE",
        "season": "2025-26",
        "fixture_id": "123",
        "lineup": [
            {
                "player": {
                    "source_player_id": source_player_id,
                    "name": "Source Starter",
                    "player_match_source_player_id": "pm-501",
                },
                "side": "home",
                "position": "MID",
                "shirt_number": "8",
                "placement": None,
                "source_formation_order": source_formation_order,
                "participation": None,
                "minutes": None,
                "provenance": {"source_family": "pulselive_match_lineups"},
            }
        ],
        "formation": {
            "home": {"status": "AVAILABLE", "value": "4-3-3"},
            "away": {"status": "UNAVAILABLE", "value": None},
        },
        "coverage": {"lineup": {"status": "AVAILABLE", "count": 1}},
        "limitations": [],
        "provenance": {},
    }


def test_source_formation_membership_preserves_starting_xi_without_player_match(monkeypatch):
    monkeypatch.setattr(
        access,
        "fixture_evidence",
        lambda season, fixture_id: _source_evidence(
            source_formation_order={
                "line_index": 2,
                "slot_index": 1,
                "line_size": 3,
            }
        ),
    )
    monkeypatch.setattr(access, "_ura_player_rows", lambda season, fixture_id: {})
    monkeypatch.setattr(
        access,
        "_player_match_lookup_identity",
        lambda season, fixture_id, row: ("", None),
    )

    result = access.fixture_research_result("2025-26", "123")

    player = result["lineup"][0]
    assert player["participation"] == "starting"
    assert player["participation_evidence"] == "PULSELIVE_FORMATION_LINEUP"
    assert player["provenance"]["participation_evidence"] == "PULSELIVE_FORMATION_LINEUP"
    assert result["coverage"]["lineup"]["starting"] == 1
    assert result["coverage"]["lineup"]["unknown"] == 0
    assert not any("participation remains unknown" in item for item in result["limitations"])


def test_player_without_enrichment_or_source_formation_membership_remains_unknown(monkeypatch):
    monkeypatch.setattr(
        access,
        "fixture_evidence",
        lambda season, fixture_id: _source_evidence(
            source_player_id="502",
            source_formation_order=None,
        ),
    )
    monkeypatch.setattr(access, "_ura_player_rows", lambda season, fixture_id: {})
    monkeypatch.setattr(
        access,
        "_player_match_lookup_identity",
        lambda season, fixture_id, row: ("", None),
    )

    result = access.fixture_research_result("2025-26", "123")

    player = result["lineup"][0]
    assert player["participation"] == "unknown"
    assert player["participation_evidence"] == "UNAVAILABLE"
    assert result["coverage"]["lineup"]["unknown"] == 1
    assert any("participation remains unknown" in item for item in result["limitations"])


def test_source_formation_starter_survives_player_match_enrichment_exception(monkeypatch):
    monkeypatch.setattr(
        access,
        "fixture_evidence",
        lambda season, fixture_id: _source_evidence(
            source_formation_order={
                "line_index": 2,
                "slot_index": 1,
                "line_size": 3,
            }
        ),
    )

    def enrichment_failure(season, fixture_id):
        raise FileNotFoundError("optional player-match season unavailable")

    def unexpected_lookup(*args, **kwargs):
        raise AssertionError("identity enrichment should be skipped after optional enrichment failure")

    monkeypatch.setattr(access, "_ura_player_rows", enrichment_failure)
    monkeypatch.setattr(access, "_player_match_lookup_identity", unexpected_lookup)

    result = access.fixture_research_result("2025-26", "123")

    player = result["lineup"][0]
    assert player["participation"] == "starting"
    assert player["participation_evidence"] == "PULSELIVE_FORMATION_LINEUP"
    assert result["coverage"]["lineup"]["starting"] == 1
    assert result["provenance"]["player_match_access"] is False
    assert result["provenance"]["player_match_enrichment"] == {
        "status": "UNAVAILABLE",
        "failure_type": "FileNotFoundError",
    }
    assert any(
        "Player-Match participation enrichment was unavailable" in item
        for item in result["limitations"]
    )
