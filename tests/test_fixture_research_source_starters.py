from __future__ import annotations

import fixture_research_access as access


def test_source_formation_membership_preserves_starting_xi_without_player_match(monkeypatch):
    monkeypatch.setattr(
        access,
        "fixture_evidence",
        lambda season, fixture_id: {
            "status": "AVAILABLE",
            "season": season,
            "fixture_id": str(fixture_id),
            "lineup": [
                {
                    "player": {"source_player_id": "501", "name": "Source Starter"},
                    "side": "home",
                    "position": "MID",
                    "shirt_number": "8",
                    "placement": None,
                    "source_formation_order": {
                        "line_index": 2,
                        "slot_index": 1,
                        "line_size": 3,
                    },
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
        },
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
        lambda season, fixture_id: {
            "status": "AVAILABLE",
            "season": season,
            "fixture_id": str(fixture_id),
            "lineup": [
                {
                    "player": {"source_player_id": "502", "name": "Unclassified Player"},
                    "side": "home",
                    "position": "MID",
                    "shirt_number": "12",
                    "placement": None,
                    "source_formation_order": None,
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
        },
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
