"""Read-only access to the authoritative FRL canonical variable catalogue."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT / "data" / "frl_canonical_variable_dictionary_v1.csv"


def load_catalogue() -> tuple[dict[str, str], ...]:
    if not CATALOGUE.exists():
        raise FileNotFoundError(f"Canonical variable catalogue not found: {CATALOGUE}")

    with CATALOGUE.open("r", encoding="utf-8-sig", newline="") as fh:
        return tuple(csv.DictReader(fh))


def canonical_variables() -> tuple[dict[str, str], ...]:
    return load_catalogue()


def find_variable(name: str) -> dict[str, str] | None:
    target = name.strip().lower()
    for row in load_catalogue():
        if (row.get("field_name") or "").strip().lower() == target:
            return row
    return None


__all__ = ["canonical_variables", "find_variable", "load_catalogue"]
