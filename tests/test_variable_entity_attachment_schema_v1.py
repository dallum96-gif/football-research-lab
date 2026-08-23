from materialize_variable_entity_attachment_schema_v1 import _player_match, _player_season, _status, _team_match, _variable_map


def test_status_vocabulary_is_normalized():
    assert _status("VERIFIED_SOURCE_MATCH_ROUTE") == "VERIFIED"
    assert _status("AMBIGUOUS_OR_MISSING") == "REVIEW"
    assert _status("SOURCE_NATIVE_ONLY") == "UNRESOLVED"
    assert _status("NOT_APPLICABLE") == "NOT_APPLICABLE"


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
            "home_team_attachment_status": "NOT_APPLICABLE",
            "away_team_attachment_status": "NOT_APPLICABLE",
        }
    ])
    row = rows[0]
    assert row["fixture_attachment_status"] == "VERIFIED"
    assert row["fixture_entity_id"] == "f2"
    assert row["team_attachment_status"] == "VERIFIED"


def test_player_season_schema_keeps_fixture_not_applicable():
    rows = _player_season([
        {
            "observation_id": "ps-1",
            "season": "2025-26",
            "source_player_id": "p1",
            "player_attachment_status": "SOURCE_NATIVE_ONLY",
        }
    ])
    row = rows[0]
    assert row["fixture_attachment_status"] == "NOT_APPLICABLE"
    assert row["player_attachment_status"] == "UNRESOLVED"
