"""Context-aware discovery over the FRL source variable universe.

This is a consumer facade, not a second source adapter. It discovers native
fields empirically for the requested season and delegates value retrieval to
``variable_resolver`` and the existing generic research-field layer.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from research_field_query import available_fields
from variable_resolver import VariableDefinition, variable_definition, resolve_variable

FAMILIES = ("team_match", "player_match", "player_season", "squad")


def _families_for_context(
    *,
    fixture_id: str | None,
    team_id: str | None,
    player_id: str | None,
    family: str | None,
) -> tuple[str, ...]:
    if family is not None:
        if family not in FAMILIES:
            raise ValueError(f"Unknown FRL variable family: {family}")
        return (family,)
    if fixture_id is not None and player_id is not None:
        return ("player_match",)
    if fixture_id is not None and team_id is not None:
        return ("team_match",)
    if fixture_id is not None:
        return ("team_match", "player_match")
    if player_id is not None:
        return ("player_season", "squad")
    return FAMILIES


def list_variables(
    *,
    season: str,
    fixture_id: str | None = None,
    team_id: str | None = None,
    player_id: str | None = None,
    family: str | None = None,
) -> tuple[VariableDefinition, ...]:
    """Return variables empirically available in a requested FRL context.

    Native source fields are listed from the requested season. Canonical aliases
    that represent derived metrics are added separately where their underlying
    fields are empirically available.
    """
    selected = _families_for_context(
        fixture_id=fixture_id,
        team_id=team_id,
        player_id=player_id,
        family=family,
    )
    found: dict[tuple[str, str], VariableDefinition] = {}

    for selected_family in selected:
        for field in available_fields(selected_family, season):
            definition = variable_definition(
                field,
                family=selected_family,
                season=season,
            )
            found[(selected_family, field)] = definition

    # Add canonical derived variables only when both source inputs are present.
    derived = {
        "wonTacklePct": ("player_match", "wonTackle", "totalTackle"),
        "passCompletionPct": ("player_match", "accuratePass", "totalPass"),
    }
    for name, (derived_family, first, second) in derived.items():
        if derived_family not in selected:
            continue
        season_fields = set(available_fields(derived_family, season))
        if first in season_fields and second in season_fields:
            definition = variable_definition(name, family=derived_family, season=season)
            found[(derived_family, name)] = definition

    return tuple(
        found[key]
        for key in sorted(found, key=lambda item: (item[0], item[1]))
    )


def variable_catalogue(
    *,
    season: str,
    fixture_id: str | None = None,
    team_id: str | None = None,
    player_id: str | None = None,
    family: str | None = None,
) -> tuple[dict, ...]:
    """Return serialisable variable metadata suitable for GUI/query consumers."""
    return tuple(asdict(item) for item in list_variables(
        season=season,
        fixture_id=fixture_id,
        team_id=team_id,
        player_id=player_id,
        family=family,
    ))


def resolve_all(
    *,
    season: str,
    fixture_id: str,
    team_id: str | None = None,
    player_id: str | None = None,
    family: str | None = None,
    variables: Iterable[str] | None = None,
) -> dict[str, dict]:
    """Resolve a selected or complete context variable set.

    ``variables=None`` resolves every variable available for the requested
    context. Callers can supply a subset when a UI section needs only a few
    fields.
    """
    available = list_variables(
        season=season,
        fixture_id=fixture_id,
        team_id=team_id,
        player_id=player_id,
        family=family,
    )
    allowed = {item.name for item in available}
    selected = tuple(variables) if variables is not None else tuple(item.name for item in available)

    unknown = [name for name in selected if name not in allowed]
    if unknown:
        raise ValueError(
            "Requested variables are not available in this context/season: "
            + ", ".join(sorted(unknown))
        )

    return {
        name: resolve_variable(
            name,
            season=season,
            fixture_id=fixture_id,
            team_id=team_id,
            player_id=player_id,
            family=family,
        )
        for name in selected
    }


__all__ = ["FAMILIES", "list_variables", "variable_catalogue", "resolve_all"]
