from entity_route_inheritance import (
    relationship_contract_for,
    route_for_entity,
    routes_for_grain,
)


def test_team_match_inherits_fixture_and_team_routes():
    routes = routes_for_grain("team_match")
    assert {route.entity for route in routes} == {"FIXTURE", "TEAM"}
    assert relationship_contract_for("team_match", "FIXTURE") == "canonical_fixture_to_source_match"
    assert relationship_contract_for("team_match", "TEAM") == "canonical_team_season_to_source_team"


def test_player_match_inherits_fixture_context_and_player_observation():
    fixture = route_for_entity("player_match", "fixture")
    player = route_for_entity("player_match", "player")
    assert fixture is not None
    assert fixture.relationship_contract == "canonical_fixture_to_source_match"
    assert player is not None
    assert player.relationship_contract == "player_identity_to_player_match_observations"


def test_player_season_has_player_route_only():
    routes = routes_for_grain("player_season")
    assert len(routes) == 1
    assert routes[0].entity == "PLAYER"
    assert routes[0].relationship_contract == "source_player_identity_to_player_season"
    assert route_for_entity("player_season", "TEAM") is None


def test_squad_inherits_team_season_route():
    route = route_for_entity("squad", "TEAM")
    assert route is not None
    assert route.relationship_contract == "canonical_team_season_to_source_team"
    assert route.route_kind == "CONTEXT_INHERITANCE"


def test_unmapped_grain_has_no_inheritance_route():
    assert routes_for_grain("sample_payload") == ()
    assert route_for_entity("sample_payload", "PLAYER") is None
