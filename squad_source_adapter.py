"""Fail-closed boundary for squad source observations.

The relationship contract is established, but the current repository/audit
root does not contain a materialised squad source file. This adapter therefore
refuses to invent or infer squad rows. Once an approved squad source is
materialised, it can be wired here without changing the identity contract.
"""
from __future__ import annotations

from pathlib import Path

from relationship_contracts import get_relationship_contract

ROOT = Path(__file__).resolve().parent


def squad_source_available() -> bool:
    """Return whether an explicitly materialised squad source exists."""
    candidates = (
        ROOT / "squad",
        ROOT / "data" / "squad",
        ROOT / "sources" / "squad",
    )
    return any(path.is_dir() and any(path.iterdir()) for path in candidates)


def squad_route_status() -> str:
    """Return readiness without inferring a team identity or fabricating rows."""
    get_relationship_contract("canonical_team_season_to_source_team")
    return "SOURCE_REQUIRED" if not squad_source_available() else "SOURCE_AVAILABLE_REQUIRES_VERIFICATION"


def squad_source_rows(season: str, local_team_id: str):
    """Refuse access until an approved squad source is materialised and mapped."""
    raise RuntimeError(
        "Squad source rows are not available in the current repository materialisation; "
        "no squad identity or team-season relationship is inferred."
    )
