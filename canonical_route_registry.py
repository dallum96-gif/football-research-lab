"""Read-only access to the authoritative FRL canonical route registry.

The route registry is an additive reusable seam over the tracked route artefact.
It does not infer routes, create identities, or alter canonical variable
semantics; it only validates and exposes the existing route declarations.
"""
from __future__ import annotations

import csv
from pathlib import Path

from canonical_variable_catalogue import canonical_variables

ROOT = Path(__file__).resolve().parent
ROUTES = ROOT / "data" / "frl_canonical_variable_routes_v1.csv"


class CanonicalRouteError(ValueError):
    """Base error for invalid canonical route registry state."""


class DuplicateRouteError(CanonicalRouteError):
    pass


class OrphanRouteError(CanonicalRouteError):
    pass


def load_routes() -> tuple[dict[str, str], ...]:
    if not ROUTES.exists():
        raise FileNotFoundError(f"Canonical route registry not found: {ROUTES}")
    with ROUTES.open("r", encoding="utf-8-sig", newline="") as fh:
        return tuple(csv.DictReader(fh))


def route_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row.get("source_surface", ""),
        row.get("resource", ""),
        row.get("grain", ""),
        row.get("field_name", ""),
    )


def canonical_route_keys() -> tuple[tuple[str, str, str, str], ...]:
    return tuple(route_key(row) for row in load_routes())


def validate_route_registry() -> dict[str, int]:
    routes = load_routes()
    catalogue = canonical_variables()
    catalogue_keys = {
        (
            row.get("source_surface", ""),
            row.get("resource", ""),
            row.get("grain", ""),
            row.get("field_name", ""),
        )
        for row in catalogue
    }

    keys = [route_key(row) for row in routes]
    duplicates = len(keys) - len(set(keys))
    if duplicates:
        raise DuplicateRouteError(f"Canonical route registry contains {duplicates} duplicate route keys")

    orphans = sum(key not in catalogue_keys for key in keys)
    if orphans:
        raise OrphanRouteError(f"Canonical route registry contains {orphans} routes absent from the canonical catalogue")

    return {
        "canonical_variables": len(catalogue),
        "unique_routes": len(routes),
        "orphan_routes": 0,
        "unrouted_variables": len(catalogue) - len(routes),
    }


__all__ = [
    "CanonicalRouteError",
    "DuplicateRouteError",
    "OrphanRouteError",
    "canonical_route_keys",
    "load_routes",
    "route_key",
    "validate_route_registry",
]
