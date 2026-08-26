from variable_catalog import VARIABLES
from variable_resolver import (
    VariableResolver,
    VariableResolutionError,
    VariableDefinition,
)


def test_catalog_contains_selected_player_match_variables():
    names = {item.name for item in VARIABLES}
    assert {
        "wonTacklePct",
        "interceptionWon",
        "passCompletionPct",
        "keyPass",
        "successfulDribbles",
        "onTargetScoringAttempt",
    } <= names


def test_catalog_marks_selected_variables_gui_accessible():
    assert all(item.status == "GUI_ACCESSIBLE" for item in VARIABLES)
    assert all(item.grain == "player_fixture" for item in VARIABLES)


def test_resolver_rejects_unknown_variable():
    resolver = VariableResolver()
    try:
        resolver.resolve("doesNotExist")
    except VariableResolutionError as exc:
        assert "Unknown FRL variable" in str(exc)
    else:
        raise AssertionError("Unknown variable was not rejected")


def test_resolver_rejects_gui_variable_without_handler():
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
        raise AssertionError("Unresolvable variable was not rejected")


def test_resolver_returns_structured_result():
    resolver = VariableResolver()
    resolver.register(
        VariableDefinition(
            name="successfulDribbles",
            label="Successful dribbles",
            grain="player_fixture",
            status="GUI_ACCESSIBLE",
            resolver="player_match",
            source_family="player_match",
            source_field="successfulDribbles",
        ),
        lambda **context: [{"player": "Test Player", "value": 2}],
    )

    result = resolver.resolve(
        "successfulDribbles",
        fixture=("2024-25", 1),
    ).as_dict()

    assert result["variable"] == "successfulDribbles"
    assert result["status"] == "RESOLVED"
    assert result["values"][0]["value"] == 2
    assert result["source"]["field"] == "successfulDribbles"
