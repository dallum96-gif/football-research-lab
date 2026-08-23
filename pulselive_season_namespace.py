"""Audited Pulselive season-id namespace mapping.

Mappings in this module are provenance-backed external corroboration, not raw
FRL source truth. Callers may use them only where the mapping status is
explicitly recorded as EXTERNAL_CORROBORATED.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAP_FILE = ROOT / "identity" / "provenance" / "pulselive_season_namespace_map.csv"


def load_mapping(path: Path = MAP_FILE) -> dict[str, str]:
    if not path.is_file():
        return {}
    mapping: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("status") != "EXTERNAL_CORROBORATED":
                continue
            source_id = str(row.get("source_season_id") or "").strip()
            frl_season = str(row.get("frl_season") or "").strip()
            if source_id and frl_season:
                mapping[source_id] = frl_season
    return mapping
