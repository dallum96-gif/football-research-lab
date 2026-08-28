"""Universal FRL research access seam."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from canonical_variable_catalogue import canonical_variables
from fpl_variable_access import (
    FPLVariableUnavailableError,
    fpl_catalogue,
    _load as _fpl_load,
    _source_field as _fpl_source_field,
)
from research_field_query import (
    player_match_source_fields,
    player_season_source_fields,
    player_season_source_rows,
    squad_source_fields,
    squad_source_rows,
    team_match_source_fields,
)
from source_family_adapters import (
    player_match_source_rows_for_season,
    team_match_source_rows_for_season,
)
from variable_resolver import (
    VariableResolutionError,
    resolve_variable,
    variable_definition,
)

CORE_FAMILIES = ("team_match", "player_match", "player_season", "squad")
ALL_FAMILIES = CORE_FAMILIES + ("fpl",)
ACCESS_VERSION = "0.3.2"


class ResearchAccessError(ValueError):
    """Base error for invalid research-access requests."""


@dataclass(frozen=True)
class ResearchRequest:
    variable: str
    season: str
    family: str | None = None
    fixture_id: str | None = None
    team_id: str | None = None
    player_id: str | None = None
    gameweek: str | None = None
    as_of_date: str | None = None
    information_available_as_of: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def resolver_dict(self) -> dict[str, Any]:
        data = self.as_dict()
        data.pop("as_of_date", None)
        data.pop("information_available_as_of", None)
        data["name"] = data.pop("variable")
        return data


def _catalogue_family(row: dict[str, str]) -> str:
    """Map the canonical catalogue's relationship/grain metadata to a consumer family."""
    grain = str(row.get("grain") or "").strip()
    if grain in CORE_FAMILIES:
        return grain
    relationship = str(row.get("relationship") or "").strip()
    if relationship in CORE_FAMILIES:
        return relationship
    attachment = str(row.get("canonical_attachment") or "").strip()
    mapping = {
        "player_fixture": "player_match",
        "team_fixture": "team_match",
        "player_season": "player_season",
        "squad": "squad",
    }
    return mapping.get(attachment, "")


def _core_capabilities() -> tuple[dict[str, Any], ...]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for row in canonical_variables():
        family = _catalogue_family(row)
        name = str(row.get("field_name") or "").strip()
        if family not in CORE_FAMILIES or not name:
            continue
        rows[(family, name)] = {
            "variable": name,
            "family": family,
            "label": row.get("label") or name,
            "status": row.get("semantic_status") or row.get("status") or "catalogued",
            "source_field": name,
            "provenance": {"registry": "FRL canonical variable catalogue"},
        }
    return tuple(sorted(rows.values(), key=lambda item: (item["family"], item["variable"])))


def _fpl_capabilities() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "variable": row.get("field_name", ""),
            "family": "fpl",
            "label": row.get("field_name", ""),
            "subclass": row.get("subclass"),
            "status": row.get("semantic_status") or row.get("status") or "research_exposed",
            "source_field": row.get("field_name", ""),
            "provenance": {"registry": "authoritative FPL variable registry"},
        }
        for row in fpl_catalogue()
    )


def discover(*, family: str | None = None, search: str | None = None) -> dict[str, Any]:
    """Discover research capabilities without exposing storage details."""
    if family is not None and family not in ALL_FAMILIES:
        raise ResearchAccessError(f"Unknown research family: {family}")

    if family == "fpl":
        capabilities = _fpl_capabilities()
    elif family in CORE_FAMILIES:
        capabilities = tuple(item for item in _core_capabilities() if item["family"] == family)
    else:
        capabilities = _core_capabilities() + _fpl_capabilities()

    if search:
        target = search.strip().casefold()
        capabilities = tuple(
            item
            for item in capabilities
            if target in str(item.get("variable", "")).casefold()
            or target in str(item.get("label", "")).casefold()
            or target in str(item.get("subclass", "")).casefold()
        )

    return {
        "query_type": "capability_discovery",
        "access_version": ACCESS_VERSION,
        "family": family,
        "search": search,
        "count": len(capabilities),
        "results": list(capabilities),
        "provenance": {
            "core_registry": "FRL canonical variable catalogue",
            "fpl_registry": "authoritative FPL variable registry",
        },
        "temporal_note": "Capability discovery describes what the registry exposes; it does not establish evidence coverage or historical information availability.",
    }


def _temporal_context(request: ResearchRequest) -> dict[str, Any]:
    return {
        "season_state_requested": request.season,
        "as_of_date": request.as_of_date,
        "information_available_as_of": request.information_available_as_of,
        "historical_state_and_information_availability_distinct": True,
        "information_availability_status": (
            "requested" if request.information_available_as_of else "not_assessed"
        ),
    }


def _provenance_context(definition: Any) -> dict[str, Any]:
    return {
        "variable": definition.name,
        "family": definition.family,
        "source_field": definition.source_field,
        "status": definition.status,
        "canonical_registry": "FRL canonical variable catalogue" if definition.family != "fpl" else "authoritative FPL variable registry",
        "access_layer": "FRL universal research access",
    }


def validate(request: ResearchRequest) -> dict[str, Any]:
    """Validate a research request without executing evidence retrieval."""
    variable = request.variable.strip() if isinstance(request.variable, str) else ""
    season = request.season.strip() if isinstance(request.season, str) else ""
    if not variable:
        raise ResearchAccessError("variable is required")
    if not season:
        raise ResearchAccessError("season is required")
    if request.family is not None and request.family not in ALL_FAMILIES:
        raise ResearchAccessError(f"Unknown research family: {request.family}")

    for field_name, value in {
        "fixture_id": request.fixture_id,
        "team_id": request.team_id,
        "player_id": request.player_id,
        "gameweek": request.gameweek,
    }.items():
        if value is not None and not str(value).strip():
            raise ResearchAccessError(f"{field_name} cannot be empty")

    try:
        definition = variable_definition(
            request.variable,
            family=request.family,
            season=request.season,
        )
    except (VariableResolutionError, FPLVariableUnavailableError) as exc:
        raise ResearchAccessError(str(exc)) from exc

    if definition.family in {"player_match", "team_match"} and request.fixture_id is None:
        raise ResearchAccessError(f"family '{definition.family}' requires fixture_id")
    if definition.family == "fpl" and request.player_id is None and request.fixture_id is None:
        raise ResearchAccessError("fpl research requires player_id or fixture_id")

    return {
        "valid": True,
        "request": request.as_dict(),
        "definition": {
            "name": definition.name,
            "label": definition.label,
            "family": definition.family,
            "source_field": definition.source_field,
            "status": definition.status,
        },
        "access_version": ACCESS_VERSION,
        "temporal": _temporal_context(request),
        "provenance": _provenance_context(definition),
    }


def _safe_value(value: Any) -> bool:
    return value not in (None, "", "null", "None")


def _coverage_core(family: str, season: str, field: str) -> dict[str, Any]:
    if family == "player_match":
        fields = set(player_match_source_fields(season))
        rows = player_match_source_rows_for_season(season) if field in fields else ()
    elif family == "team_match":
        fields = set(team_match_source_fields(season))
        rows = team_match_source_rows_for_season(season) if field in fields else ()
    elif family == "player_season":
        fields = set(player_season_source_fields(season))
        rows = player_season_source_rows(season) if field in fields else ()
    elif family == "squad":
        fields = set(squad_source_fields(season))
        rows = squad_source_rows(season) if field in fields else ()
    else:
        raise ResearchAccessError(f"Unsupported core family: {family}")

    if field not in fields:
        return {
            "season": season,
            "family": family,
            "variable": field,
            "field_present": False,
            "population": 0,
            "observed": 0,
            "missing": 0,
            "coverage_pct": 0.0,
        }

    populated = sum(1 for row in rows if _safe_value(row.get(field)))
    population = len(rows)
    missing = population - populated
    return {
        "season": season,
        "family": family,
        "variable": field,
        "field_present": True,
        "population": population,
        "observed": populated,
        "missing": missing,
        "coverage_pct": round((populated / population) * 100.0, 3) if population else 0.0,
    }


def _coverage_fpl(season: str, field: str) -> dict[str, Any]:
    definitions = {row.get("field_name") for row in fpl_catalogue()}
    if field not in definitions:
        return {
            "season": season,
            "family": "fpl",
            "variable": field,
            "field_present": False,
            "population": 0,
            "observed": 0,
            "missing": 0,
            "coverage_pct": 0.0,
        }

    rows = _fpl_load(Path(__file__).resolve().parent / "data" / "fpl_player_gw_evidence.csv")
    candidate = tuple(row for row in rows if str(row.get("frl_season", "")) == season)
    source_key = f"source_{_fpl_source_field(field)}"
    population = len(candidate)
    observed = sum(1 for row in candidate if _safe_value(row.get(source_key)))
    missing = population - observed
    return {
        "season": season,
        "family": "fpl",
        "variable": field,
        "field_present": True,
        "population": population,
        "observed": observed,
        "missing": missing,
        "coverage_pct": round((observed / population) * 100.0, 3) if population else 0.0,
    }


def coverage(*, variable: str, seasons: list[str] | tuple[str, ...], family: str | None = None) -> dict[str, Any]:
    """Return season-by-season evidence coverage for one research variable."""
    if not seasons:
        raise ResearchAccessError("at least one season is required")

    rows: list[dict[str, Any]] = []
    definitions: list[Any] = []
    for season in seasons:
        try:
            definition = variable_definition(variable, family=family, season=season)
        except (VariableResolutionError, FPLVariableUnavailableError) as exc:
            raise ResearchAccessError(str(exc)) from exc
        definitions.append(definition)
        if definition.family == "fpl":
            row = _coverage_fpl(season, definition.source_field or definition.name)
        else:
            row = _coverage_core(definition.family, season, definition.source_field or definition.name)
        rows.append(row)

    population = sum(row["population"] for row in rows)
    observed = sum(row["observed"] for row in rows)
    missing = sum(row["missing"] for row in rows)
    seasons_with_field = sum(1 for row in rows if row["field_present"])
    seasons_with_observations = sum(1 for row in rows if row["observed"] > 0)

    provenance = _provenance_context(definitions[0])
    return {
        "query_type": "research_coverage",
        "access_version": ACCESS_VERSION,
        "variable": variable,
        "family": rows[0]["family"] if rows else family,
        "seasons_requested": list(seasons),
        "season_count": len(rows),
        "seasons_with_field": seasons_with_field,
        "seasons_with_observations": seasons_with_observations,
        "population": population,
        "observed": observed,
        "missing": missing,
        "coverage_pct": round((observed / population) * 100.0, 3) if population else 0.0,
        "results": rows,
        "provenance": {
            **provenance,
            "method": "existing FRL source-family evidence adapters",
            "no_identity_inference": True,
        },
        "temporal": {
            "seasons_requested": list(seasons),
            "historical_state_and_information_availability_distinct": True,
            "information_availability_status": "not_assessed",
        },
        "temporal_note": "Coverage describes evidence present in each declared season; it does not by itself establish historical information availability time.",
    }


def query(request: ResearchRequest) -> dict[str, Any]:
    """Execute a governed research request through the existing resolver."""
    validation = validate(request)
    raw = resolve_variable(**request.resolver_dict())
    return {
        "query_type": "research_access",
        "access_version": ACCESS_VERSION,
        "request": request.as_dict(),
        "definition": validation["definition"],
        "results": raw.get("results", []),
        "coverage": raw.get("coverage"),
        "population": raw.get("population"),
        "source_rows": raw.get("source_rows"),
        "temporal": validation["temporal"],
        "temporal_note": raw.get("temporal_note") or "Historical state and information availability are distinct; information availability is not inferred from source evidence alone.",
        "limitations": raw.get("limitations", []),
        "provenance": {
            **validation["provenance"],
            **raw.get("provenance", {}),
        },
    }


__all__ = [
    "ACCESS_VERSION",
    "ALL_FAMILIES",
    "CORE_FAMILIES",
    "ResearchAccessError",
    "ResearchRequest",
    "coverage",
    "discover",
    "query",
    "validate",
]
