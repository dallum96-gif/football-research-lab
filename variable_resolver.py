"""Universal FRL variable runtime resolution.

The resolver is a thin consumer seam over the existing generic research-field
query layer. It deliberately does not create source-specific extraction or
identity joins of its own.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from research_field_query import (
    fixture_field_values,
    player_match_field_values,
    player_season_field_values,
    squad_field_values,
)
from source_field_registry import fields_for_family


class VariableResolutionError(ValueError):
    """Base error for fail-closed variable resolution."""


class UnknownVariableError(VariableResolutionError):
    pass


class UnsupportedContextError(VariableResolutionError):
    pass


class VariableUnavailableError(VariableResolutionError):
    pass


@dataclass(frozen=True)
class VariableDefinition:
    name: str
    label: str
    family: str
    source_field: str | None = None
    derived_from: tuple[str, ...] = ()
    status: str = "exposed"
    definition: str | None = None


# The canonical aliases are deliberately small and explicit. All other
# registered source fields remain directly requestable by their native field
# name, subject to the family/context supplied by the caller.
ALIASES: dict[str, VariableDefinition] = {
    "wonTacklePct": VariableDefinition(
        name="wonTacklePct",
        label="Tackle won %",
        family="player_match",
        derived_from=("wonTackle", "totalTackle"),
        definition="Percentage of attempted tackles won.",
    ),
    "passCompletionPct": VariableDefinition(
        name="passCompletionPct",
        label="Pass completion %",
        family="player_match",
        derived_from=("accuratePass", "totalPass"),
        definition="Percentage of attempted passes completed.",
    ),
    "interceptionWon": VariableDefinition(
        name="interceptionWon",
        label="Interceptions won",
        family="player_match",
        source_field="interceptionWon",
        definition="Interceptions credited to the player in the fixture.",
    ),
    "keyPass": VariableDefinition(
        name="keyPass",
        label="Key passes",
        family="player_match",
        source_field="keyPass",
        definition="Key passes credited to the player in the fixture.",
    ),
    "successfulDribbles": VariableDefinition(
        name="successfulDribbles",
        label="Successful dribbles",
        family="player_match",
        source_field="successfulDribbles",
        definition="Successful dribbles credited to the player in the fixture.",
    ),
    "onTargetScoringAttempt": VariableDefinition(
        name="onTargetScoringAttempt",
        label="Shots on target",
        family="player_match",
        source_field="onTargetScoringAttempt",
        definition="Player scoring attempts recorded as on target.",
    ),
}


def _field_families(field: str) -> tuple[str, ...]:
    return tuple(spec.family for spec in _all_specs() if spec.source_field == field)


def _all_specs():
    for family in ("team_match", "player_match", "player_season", "squad"):
        yield from fields_for_family(family)


def _infer_definition(name: str, family: str | None) -> VariableDefinition:
    alias = ALIASES.get(name)
    if alias is not None:
        if family is not None and family != alias.family:
            raise UnsupportedContextError(
                f"Variable '{name}' belongs to {alias.family}, not {family}."
            )
        return alias

    families = _field_families(name)
    if family is not None:
        if family not in families:
            raise UnknownVariableError(
                f"Variable/source field '{name}' is not registered for family '{family}'."
            )
        return VariableDefinition(name=name, label=name, family=family, source_field=name)

    if not families:
        raise UnknownVariableError(f"Unknown FRL variable/source field: {name}")
    if len(families) > 1:
        raise UnsupportedContextError(
            f"Variable '{name}' exists in multiple source families {list(families)}; "
            "supply an explicit family or an entity context."
        )
    return VariableDefinition(name=name, label=name, family=families[0], source_field=name)


def variable_definition(name: str, *, family: str | None = None) -> VariableDefinition:
    return _infer_definition(name, family)


def _numbers(result: Mapping[str, Any], fields: tuple[str, ...]) -> dict[str, dict[str, float | None]]:
    values: dict[str, dict[str, float | None]] = {}
    by_identity = {str(item.get("source_player_id", "")): item for item in result.get("results", [])}
    for key, item in by_identity.items():
        values[key] = {}
        for field in fields:
            try:
                raw = item.get(field)
                values[key][field] = float(raw) if raw not in (None, "") else None
            except (TypeError, ValueError):
                values[key][field] = None
    return values


def _derive_player_match(
    season: str,
    fixture_id: str,
    metric: VariableDefinition,
    *,
    player_id: str | None,
) -> dict:
    rows = player_match_field_values(
        season,
        fixture_id,
        metric.derived_from[0],
        player_id=player_id,
    )["results"]
    second = player_match_field_values(
        season,
        fixture_id,
        metric.derived_from[1],
        player_id=player_id,
    )["results"]
    second_by_player = {str(item["source_player_id"]): item for item in second}
    results = []
    for item in rows:
        pid = str(item["source_player_id"])
        a_raw = item.get("value")
        b_raw = second_by_player.get(pid, {}).get("value")
        try:
            a = float(a_raw) if a_raw not in (None, "") else None
            b = float(b_raw) if b_raw not in (None, "") else None
        except (TypeError, ValueError):
            a, b = None, None
        value = None if b in (None, 0) or a is None else a / b * 100.0
        results.append(
            {
                "season": season,
                "fixture_id": str(fixture_id),
                "source_player_id": pid,
                "source_field": metric.name,
                "value": value,
                "inputs": {metric.derived_from[0]: a, metric.derived_from[1]: b},
            }
        )
    return {
        "query_type": "frl_variable",
        "variable": metric.name,
        "label": metric.label,
        "family": metric.family,
        "season": season,
        "fixture_id": str(fixture_id),
        "results": results,
        "provenance": {"source_fields": list(metric.derived_from)},
    }


def resolve_variable(
    name: str,
    *,
    season: str,
    fixture_id: str | None = None,
    team_id: str | None = None,
    player_id: str | None = None,
    family: str | None = None,
) -> dict:
    """Resolve a source/canonical variable in a football context.

    The caller may start from a fixture and optionally narrow to team/player.
    The resolver then delegates to the existing generic research-field query
    functions and returns their provenance-bearing result.
    """
    definition = variable_definition(name, family=family)

    if definition.status != "exposed":
        raise VariableUnavailableError(
            f"Variable '{name}' is not exposed for reusable consumer access."
        )

    if definition.family == "player_match":
        if fixture_id is None:
            raise UnsupportedContextError("player_match resolution requires fixture_id")
        if definition.derived_from:
            return _derive_player_match(
                season,
                str(fixture_id),
                definition,
                player_id=player_id,
            )
        return player_match_field_values(
            season,
            str(fixture_id),
            definition.source_field or definition.name,
            player_id=player_id,
        )

    if definition.family == "team_match":
        if fixture_id is None:
            raise UnsupportedContextError("team_match resolution requires fixture_id")
        return fixture_field_values(
            season,
            str(fixture_id),
            definition.source_field or definition.name,
            team_id=team_id,
        )

    if definition.family == "player_season":
        return player_season_field_values(
            season,
            definition.source_field or definition.name,
            player_id=player_id,
        )

    if definition.family == "squad":
        return squad_field_values(
            season,
            definition.source_field or definition.name,
            player_id=player_id,
        )

    raise UnsupportedContextError(f"Unsupported variable family: {definition.family}")


__all__ = ["VariableDefinition", "VariableResolutionError", "resolve_variable", "variable_definition"]
