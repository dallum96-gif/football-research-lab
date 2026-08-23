from materialize_variable_entity_attachment_schema_v1 import _player_match, _player_season, _team_match, _variable_map


def test_player_match_schema_preserves_independent_edges():
    rows = _player_match([
        {
            "observation_id": "obs-1",
            "season": "2025-26",
            "fixture_id": "f1",
            "source_match_id": "m1",
            "source_player_id": "p1",
            "fixture_attachment_status": "VERIFIED",
            "player_attachment_status": "UNRESOLVED",
            "home_team_attachment_status": "VERIFIED",
            "home_team_attachment_entity_id": "ht1",
            "away_team_attachment_status": "VERIFIED",
            "away_team_attachment_entity_id": "at1",
        }
    ])
    row = rows[0]
    assert row["fixture_attachment_status"] == "VERIFIED"
    assert row["home_team_attachment_status"] == "VERIFIED"
    assert row["away_team_attachment_status"] == "VERIFIED"
    assert row["player_attachment_status"] == "UNRESOLVED"


def test_variable_map_keeps_grain_and_contract():
    rows = _variable_map([
        {
            "field_name": "goals",
            "source_family": "fpl",
            "resource": "element",
            "grain": "player_season",
            "field_type": "numeric",
            "semantic_status": "retained",
            "relationship_kind": "OBSERVATION",
            "source_identity_required": "TRUE",
            "provenance_requirement": "SOURCE_ID_REQUIRED",
            "identity_contract": "source_player_identity_to_player_season",
        }
    ])
    assert rows[0]["grain"] == "player_season"
    assert rows[0]["identity_contract"] == "source_player_identity_to_player_season"


def test_team_match_schema_has_fixture_and_team_edges():
    rows = _team_match([
        {
            "season": "2025-26",
            "fixture_id": "f2",
            "source_match_id": "m2",
            "source_team_id": "14",
            "fixture_attachment_status": "VERIFIED_SOURCE_MATCH_ROUTE",
            "team_attachment_status": "VERIFIED",
            "home_team_attachment_status": "VERIFIED",
            "home_team_attachment_entity_id": "ts-home",
        }
    ])
    row = rows[0]
    assert row["fixture_entity_id"] == "f2"
    assert row["team_attachment_status"] == "VERIFIED"
