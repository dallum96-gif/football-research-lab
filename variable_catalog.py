"""Initial canonical variable catalogue used by the universal resolver.

The catalogue is deliberately small in executable form: it establishes the
standard metadata shape and the first validated player-match display variables.
The broader empirical source census remains the authoritative discovery layer.
"""
from __future__ import annotations

from variable_resolver import VariableDefinition, register_variable


PLAYER_MATCH_DECADE = "2016-17 through 2025-26"


VARIABLES = (
    VariableDefinition(
        name="wonTacklePct",
        label="Tackle won %",
        definition="Percentage of attempted tackles that were won.",
        grain="player_fixture",
        status="GUI_ACCESSIBLE",
        resolver="player_match",
        source_family="player_match",
        value_type="float",
        unit="percent",
        coverage=PLAYER_MATCH_DECADE,
        derived_from=("wonTackle", "totalTackle"),
    ),
    VariableDefinition(
        name="interceptionWon",
        label="Interceptions won",
        definition="Number of interceptions credited to the player in the fixture.",
        grain="player_fixture",
        status="GUI_ACCESSIBLE",
        resolver="player_match",
        source_family="player_match",
        source_field="interceptionWon",
        value_type="integer",
        coverage=PLAYER_MATCH_DECADE,
    ),
    VariableDefinition(
        name="passCompletionPct",
        label="Pass completion %",
        definition="Percentage of attempted passes completed successfully.",
        grain="player_fixture",
        status="GUI_ACCESSIBLE",
        resolver="player_match",
        source_family="player_match",
        value_type="float",
        unit="percent",
        coverage=PLAYER_MATCH_DECADE,
        derived_from=("accuratePass", "totalPass"),
    ),
    VariableDefinition(
        name="keyPass",
        label="Key passes",
        definition="Passes credited as creating a scoring opportunity.",
        grain="player_fixture",
        status="GUI_ACCESSIBLE",
        resolver="player_match",
        source_family="player_match",
        source_field="keyPass",
        value_type="integer",
        coverage=PLAYER_MATCH_DECADE,
    ),
    VariableDefinition(
        name="successfulDribbles",
        label="Successful dribbles",
        definition="Successful dribbles credited to the player in the fixture.",
        grain="player_fixture",
        status="GUI_ACCESSIBLE",
        resolver="player_match",
        source_family="player_match",
        source_field="successfulDribbles",
        value_type="integer",
        coverage=PLAYER_MATCH_DECADE,
    ),
    VariableDefinition(
        name="onTargetScoringAttempt",
        label="Shots on target",
        definition="Player scoring attempts recorded as on target.",
        grain="player_fixture",
        status="GUI_ACCESSIBLE",
        resolver="player_match",
        source_family="player_match",
        source_field="onTargetScoringAttempt",
        value_type="integer",
        coverage=PLAYER_MATCH_DECADE,
    ),
)

for _definition in VARIABLES:
    register_variable(_definition)


__all__ = ["VARIABLES"]
