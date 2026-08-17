from __future__ import annotations

from pathlib import Path

from tools.data_platform_proof import run_proof


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_merged" / "players" / "2025-26_all_players_gw.csv"


def test_parquet_round_trip_preserves_core_invariants() -> None:
    result = run_proof(SOURCE)
    assert result["rows"] > 0
    assert result["columns"] > 0
