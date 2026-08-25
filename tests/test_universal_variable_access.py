from variable_resolver import VariableDefinition, VariableResolver, VariableResolutionError
from variable_context import (
    FixtureContext,
    TeamFixtureContext,
    PlayerFixtureContext,
    PlayerSeasonContext,
    TeamSeasonContext,
    EventContext,
)


def test_contexts_are_explicit_and_hashable():
    assert FixtureContext("2024-25", 1).fixture_id == 1
    assert TeamFixtureContext("2024-25", 1, "ARS").persistent_team_code == "ARS"
    assert PlayerFixtureContext("2024-25", 1, "player-1").canonical_player_id == "player-1"
    assert PlayerSeasonContext("2024-25", "player-1").season == "2024-25"
    assert TeamSeasonContext("2024-25", "ARS").persistent_team_code == "ARS"
    assert EventContext("2024-25", 1, "event-1").source_event_identity == "event-1"


def test_fixture_to_team_to_player_handler_context_is_not_source_specific():
    calls = []

    definition = VariableDefinition(
        name="successfulDribbles",
        label="Successful dribbles",
        grain="player_fixture",
        status="GUI_ACCESSIBLE",
        resolver="player_match",
        source_family="player_match",
        source_field="successfulDribbles",
    )

    def handler(**context):
        calls.append(context)
        assert context["fixture"] == ("2024-25", 1)
        assert context["team"] == "ARS"
        return [{"player": "player-1", "value": 2}]

    resolver = VariableResolver()
    resolver.register(definition, handler)
    result = resolver.resolve(
        "successfulDribbles",
        fixture=("2024-25", 1),
        team="ARS",
    ).as_dict()

    assert result["values"] == [{"player": "player-1", "value": 2}]
    assert calls


def test_unresolvable_variable_fails_closed():
    resolver = VariableResolver()
    resolver.register(
        VariableDefinition(
            name="successfulDribbles",
            label="Successful dribbles",
            grain="player_fixture",
            status="GUI_ACCESSIBLE",
            resolver="player_match",
        )
    )
    try:
        resolver.resolve("successfulDribbles", fixture=("2024-25", 1))
    except VariableResolutionError as exc:
        assert "no registered resolution handler" in str(exc)
    else:
        raise AssertionError("Unresolvable variable did not fail closed")
