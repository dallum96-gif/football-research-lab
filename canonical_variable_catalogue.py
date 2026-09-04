"""Read-only access to the authoritative FRL canonical variable catalogue.

The CSV is the broad empirical/canonical inventory. Semantic promotion is a
separate governed decision held in ``source_field_registry``. Runtime reads
therefore overlay the current registry status so discovery cannot drift behind
an approved promotion merely because the generated catalogue snapshot predates
that decision.
"""
from __future__ import annotations

import csv
from pathlib import Path

from source_field_registry import fields_for_family

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT / "data" / "frl_canonical_variable_dictionary_v1.csv"
SEMANTIC_FAMILIES = ("team_match", "player_match", "player_season", "squad")


def _semantic_status_overlay() -> dict[tuple[str, str], str]:
    return {
        (family, spec.source_field): spec.semantic_status
        for family in SEMANTIC_FAMILIES
        for spec in fields_for_family(family)
    }


def load_catalogue() -> tuple[dict[str, str], ...]:
    if not CATALOGUE.exists():
        raise FileNotFoundError(f"Canonical variable catalogue not found: {CATALOGUE}")

    with CATALOGUE.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    semantic_status = _semantic_status_overlay()
    for row in rows:
        family = str(row.get("grain") or "").strip()
        field = str(row.get("field_name") or "").strip()
        promoted = semantic_status.get((family, field))
        if promoted:
            row["semantic_status"] = promoted

    return tuple(rows)


def canonical_variables() -> tuple[dict[str, str], ...]:
    return load_catalogue()


def find_variable(name: str) -> dict[str, str] | None:
    target = name.strip().lower()
    for row in load_catalogue():
        if (row.get("field_name") or "").strip().lower() == target:
            return row
    return None


__all__ = ["canonical_variables", "find_variable", "load_catalogue"]
