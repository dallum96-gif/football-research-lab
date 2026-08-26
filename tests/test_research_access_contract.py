import pytest

import research_access


def test_blank_variable_fails_closed():
    with pytest.raises(research_access.ResearchAccessError):
        research_access.validate(research_access.ResearchRequest(variable="", season="2024-25"))


def test_unknown_family_fails_closed():
    with pytest.raises(research_access.ResearchAccessError):
        research_access.validate(
            research_access.ResearchRequest(
                variable="goals", season="2024-25", family="made_up"
            )
        )


def test_team_match_requires_fixture_context():
    with pytest.raises(research_access.ResearchAccessError):
        research_access.validate(
            research_access.ResearchRequest(
                variable="goals", season="2024-25", family="team_match"
            )
        )


def test_player_match_requires_fixture_context():
    with pytest.raises(research_access.ResearchAccessError):
        research_access.validate(
            research_access.ResearchRequest(
                variable="successfulDribbles",
                season="2024-25",
                family="player_match",
            )
        )


def test_fpl_requires_entity_context():
    with pytest.raises(research_access.ResearchAccessError):
        research_access.validate(
            research_access.ResearchRequest(
                variable="total_points", season="2024-25", family="fpl"
            )
        )


def test_discovery_unknown_family_fails_closed():
    with pytest.raises(research_access.ResearchAccessError):
        research_access.discover(family="not_a_family")


def test_coverage_requires_seasons():
    with pytest.raises(research_access.ResearchAccessError):
        research_access.coverage(variable="successfulDribbles", seasons=[])


def test_invalid_request_does_not_execute_query():
    request = research_access.ResearchRequest(
        variable="successfulDribbles",
        season="2024-25",
        family="player_match",
    )
    with pytest.raises(research_access.ResearchAccessError):
        research_access.query(request)
