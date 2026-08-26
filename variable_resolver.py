"""Universal FRL variable runtime resolution.

The resolver is a thin consumer seam over the existing generic research-field
query layer. It deliberately does not create source-specific extraction or
identity joins of its own. FPL is an isolated first-class research family
consuming the established FPL evidence access layer.
"""
from __future__ import annotations

from dataclasses import dataclass

from fpl_variable_access import fixture_values as fpl_fixture_values
from fpl_variable_access import player_gameweek_values as fpl_player_gameweek_values
from fpl_variable_access import fpl_variable_definition
from research_field_query import (
    available_fields,
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


ALIASES: dict[str, VariableDefinition] = {
    "wonTacklePct": VariableDefinition(
        name="wonTacklePct", label="Tackle won %", family="player_match",
        derived_from=("wonTackle", "totalTackle"),
        definition="Percentage of attempted tackles won.",
    ),
    "passCompletionPct": VariableDefinition(
        name="passCompletionPct", label="Pass completion %", family="player_match",
        derived_from=("accuratePass", "totalPass"),
        definition="Percentage of attempted passes completed.",
    ),
    "interceptionWon": VariableDefinition(
        name="interceptionWon", label="Interceptions won", family="player_match",
        source_field="interceptionWon",
        definition="Interceptions credited to the player in the fixture.",
    ),
    "keyPass": VariableDefinition(
        name="keyPass", label="Key passes", family="player_match",
        source_field="keyPass",
        definition="Key passes credited to the player in the fixture.",
    ),
    "successfulDribbles": VariableDefinition(
        name="successfulDribbles", label="Successful dribbles", family="player_match",
        source_field="successfulDribbles",
        definition="Successful dribbles credited to the player in the fixture.",
    ),
    "onTargetScoringAttempt": VariableDefinition(
        name="onTargetScoringAttempt", label="Shots on target", family="player_match",
        source_field="onTargetScoringAttempt",
        definition="Player scoring attempts recorded as on target.",
    ),
}


def _registered_families(field: str) -> tuple[str, ...]:
    return tuple(spec.family for spec in _all_specs() if spec.source_field == field)


def _all_specs():
    for family in ("team_match", "player_match", "player_season", "squad"):
        yield from fields_for_family(family)


def _season_families(field: str, season: str | None) -> tuple[str, ...]:
    if season is None:
        return tuple()
    return tuple(
        family
        for family in ("team_match", "player_match", "player_season", "squad")
        if field in set(available_fields(family, season))
    )


def _infer_definition(name: str, family: str | None, season: str | None) -> VariableDefinition:
    alias = ALIASES.get(name)
    if alias is not None:
        if family is not None and family != alias.family:
            raise UnsupportedContextError(
                f"Variable '{name}' belongs to {alias.family}, not {family}."
            )
        return alias

    if family == "fpl":
        row = fpl_variable_definition(name)
        return VariableDefinition(
            name=name,
            label=name,
            family="fpl",
            source_field=name,
            definition=row.get("subclass"),
        )

    families = _registered_families(name)
    if season is not None:
        discovered = _season_families(name, season)
        families = tuple(dict.fromkeys((*families, *discovered)))

    if family is not None:
        if family not in families:
            raise UnknownVariableError(
                f"Variable/source field '{name}' is not available for family '{family}' in the requested context."
            )
        return VariableDefinition(name=name, label=name, family=family, source_field=name)

    if not families:
        raise UnknownVariableError(f"Unknown FRL variable/source field: {name}")
    if len(families) > 1:
        raise UnsupportedContextError(
            f"Variable '{name}' exists in multiple source families {list(families)}; supply an explicit family or entity context."
        )
    return VariableDefinition(name=name, label=name, family=families[0], source_field=name)


def variable_definition(name: str, *, family: str | None = None, season: str | None = None) -> VariableDefinition:
    return _infer_definition(name, family, season)


def _derive_player_match(season: str, fixture_id: str, metric: VariableDefinition, *, player_id: str | None) -> dict:
    first = player_match_field_values(season, fixture_id, metric.derived_from[0], player_id=player_id)
    second = player_match_field_values(season, fixture_id, metric.derived_from[1], player_id=player_id)
    second_by_player = {str(item["source_player_id"]): item for item in second.get("results", [])}
    results = []
    for item in first.get("results", []):
        pid = str(item["source_player_id"])
        a_raw = item.get("value")
        b_raw = second_by_player.get(pid, {}).get("value")
        try:
            a = float(a_raw) if a_raw not in (None, "") else None
            b = float(b_raw) if b_raw not in (None, "") else None
        except (TypeError, ValueError):
            a, b = None, None
        value = None if b in (None, 0) or a is None else a / b * 100.0
        results.append({
            "season": season,
            "fixture_id": str(fixture_id),
            "source_player_id": pid,
            "source_field": metric.name,
            "value": value,
            "inputs": {metric.derived_from[0]: a, metric.derived_from[1]: b},
        })
    return {
        "query_type": "frl_variable", "variable": metric.name, "label": metric.label,
        "family": metric.family, "season": season, "fixture_id": str(fixture_id),
        "results": results,
        "provenance": {"source_fields": list(metric.derived_from), "registry_status": "derived"},
    }


def _native_result(*, definition: VariableDefinition, season: str, fixture_id: str | None, raw: dict) -> dict:
    """Wrap a generic research result without discarding research semantics."""
    result = {
        "query_type": "frl_variable",
        "variable": definition.name,
        "label": definition.label,
        "family": definition.family,
        "season": season,
        "fixture_id": str(fixture_id) if fixture_id is not None else None,
        "results": raw.get("results", []),
        "provenance": {
            "source_fields": [definition.source_field or definition.name],
            "registry_status": "native",
        },
    }

    # Preserve the generic research/query layer's coverage and temporal
    # semantics so downstream research/GUI consumers cannot lose them merely
    # by passing through the universal resolver.
    for key in ("coverage", "source_rows", "temporal_note", "limitations"):
        if key in raw:
            result[key] = raw[key]

    return result


def resolve_variable(
    name: str,
    *,
    season: str,
    fixture_id: str | None = None,
    team_id: str | None = None,
    player_id: str | None = None,
    gameweek: str | None = None,
    family: str | None = None,
) -> dict:
    """Resolve a source/canonical variable in a football context."""
    definition = variable_definition(name, family=family, season=season)

    if definition.status != "exposed":
        raise VariableUnavailableError(
            f"Variable '{name}' is not exposed for reusable consumer access."
        )

    if definition.family == "fpl":
        if player_id is not None:
            return fpl_player_gameweek_values(
                season=season,
                player_id=player_id,
                field_name=definition.source_field or definition.name,
                gameweek=gameweek,
            )
        if fixture_id is not None:
            return fpl_fixture_values(
                season=season,
                fixture_id=str(fixture_id),
                field_name=definition.source_field or definition.name,
            )
        raise UnsupportedContextError("fpl resolution requires player_id or fixture_id")

    if definition.family == "player_match":
        if fixture_id is None:
            raise UnsupportedContextError("player_match resolution requires fixture_id")
        if definition.derived_from:
            return _derive_player_match(season, str(fixture_id), definition, player_id=player_id)
        raw = player_match_field_values(
            season, str(fixture_id), definition.source_field or definition.name, player_id=player_id
        )
        return _native_result(definition=definition, season=season, fixture_id=fixture_id, raw=raw)

    if definition.family == "team_match":
        if fixture_id is None:
            raise UnsupportedContextError("team_match resolution requires fixture_id")
        return fixture_field_values(
            season, str(fixture_id), definition.source_field or definition.name, team_id=team_id
        )

    if definition.family == "player_season":
        raw = player_season_field_values(
            season, definition.source_field or definition.name, player_id=player_id
        )
        return _native_result(definition=definition, season=season, fixture_id=None, raw=raw)

    if definition.family == "squad":
        raw = squad_field_values(
            season, definition.source_field or definition.name, player_id=player_id
        )
        return _native_result(definition=definition, season=season, fixture_id=None, raw=raw)

    raise UnsupportedContextError(f"Unsupported variable family: {definition.family}")


__all__ = [
    "VariableDefinition",
    "VariableResolutionError",
    "resolve_variable",
    "variable_definition",
]
