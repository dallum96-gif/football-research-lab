from __future__ import annotations

from pathlib import Path

from tools.data_platform_proof import run_fixture_proof, run_player_proof


ROOT = Path(__file__).resolve().parents[1]
PLAYER_SOURCE = ROOT / "_merged" / "players" / "2025-26_all_players_gw.csv"
FIXTURE_SOURCE = ROOT / "data" / "fixture_match_stats.csv"


def test_player_parquet_round_trip_preserves_core_invariants() -> None:
    result = run_player_proof(PLAYER_SOURCE)
    assert result["rows"] > 0
    assert result["columns"] > 0


def test_fixture_parquet_round_trip_preserves_canonical_key() -> None:
    result = run_fixture_proof(FIXTURE_SOURCE)
    assert result["rows"] > 0
    assert result["duplicate_keys"] == 0
    assert result["missing_keys"] == 0
