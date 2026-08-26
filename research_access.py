"""Universal FRL research access seam.

This module is the governed consumer boundary above the existing variable
resolver and evidence adapters. It does not perform source-specific joins,
identity inference, or independent metric calculations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from canonical_variable_catalogue import canonical_variables
from fpl_variable_access import fpl_catalogue
from variable_resolver import (
    UnsupportedContextError,
    VariableResolutionError,
    resolve_variable,
    variable_definition,
)

CORE_FAMILIES = ("team_match", "player_match", "player_season", "squad")
ALL_FAMILIES = CORE_FAMILIES + ("fpl",)
ACCESS_VERSION = "0.1.0"


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

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _core_capabilities() -> tuple[dict[str, Any], ...]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for row in canonical_variables():
        family = str(row.get("family") or row.get("relationship") or "").strip()
        name = str(row.get("field_name") or "").strip()
        if family not in CORE_FAMILIES or not name:
            continue
        rows[(family, name)] = {
            "variable": name,
            "family": family,
            "label": row.get("label") or name,
            "status": row.get("semantic_status") or row.get("status") or "catalogued",
            "source_field": row.get("field_name") or name,
            "provenance": {
                "registry": "FRL canonical variable catalogue",
            },
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
            "provenance": {
                "registry": "authoritative FPL variable registry",
            },
        }
        for row in fpl_catalogue()
    )


def discover(*, family: str | None = None, search: str | None = None) -> dict[str, Any]:
    """Discover research capabilities without exposing storage details."""
    if family is not None and family not in ALL_FAMILIES:
        raise ResearchAccessError(f"Unknown research family: {family}")

    capabilities = _fpl_capabilities() if family == "fpl" else _core_capabilities() if family in CORE_FAMILIES else _core_capabilities() + _fpl_capabilities()

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
    }


def validate(request: ResearchRequest) -> dict[str, Any]:
    """Validate a research request without executing evidence retrieval."""
    if not request.variable.strip():
        raise ResearchAccessError("variable is required")
    if not request.season.strip():
        raise ResearchAccessError("season is required")
    if request.family is not None and request.family not in ALL_FAMILIES:
        raise ResearchAccessError(f"Unknown research family: {request.family}")

    try:
        definition = variable_definition(
            request.variable,
            family=request.family,
            season=request.season,
        )
    except VariableResolutionError as exc:
        raise ResearchAccessError(str(exc)) from exc

    if definition.family in {"player_match", "team_match"} and request.fixture_id is None:
        raise ResearchAccessError(
            f"family '{definition.family}' requires fixture_id"
        )
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
    }


def query(request: ResearchRequest) -> dict[str, Any]:
    """Execute a governed research request through the existing resolver."""
    validation = validate(request)
    raw = resolve_variable(**request.as_dict())

    result = {
        "query_type": "research_access",
        "access_version": ACCESS_VERSION,
        "request": request.as_dict(),
        "definition": validation["definition"],
        "results": raw.get("results", []),
        "coverage": raw.get("coverage"),
        "population": raw.get("population"),
        "source_rows": raw.get("source_rows"),
        "temporal_note": raw.get("temporal_note"),
        "limitations": raw.get("limitations", []),
        "provenance": raw.get("provenance", {}),
    }
    return result


__all__ = [
    "ACCESS_VERSION",
    "ALL_FAMILIES",
    "CORE_FAMILIES",
    "ResearchAccessError",
    "ResearchRequest",
    "discover",
    "query",
    "validate",
]
