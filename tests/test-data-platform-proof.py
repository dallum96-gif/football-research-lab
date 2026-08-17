from __future__ import annotations

from pathlib import Path

from tools.data_platform_proof import (
    DEFAULT_FIXTURE_MASTER,
    DEFAULT_FIXTURE_SOURCE,
    DEFAULT_IDENTITY_REGISTRY,
    DEFAULT_PLAYER_SOURCE,
    DEFAULT_TEAM_REGISTRY,
    run_fixture_proof,
    run_player_proof,
    run_relationship_proof,
)


def test_parquet_round_trip_preserves_player_invariants() -> None:
    result = run_player_proof(DEFAULT_PLAYER_SOURCE)
    assert result["rows"] > 0
    assert result["columns"] > 0


def test_parquet_round_trip_preserves_fixture_identity() -> None:
    result = run_fixture_proof(DEFAULT_FIXTURE_SOURCE)
    assert result["rows"] > 0
    assert result["duplicate_keys"] == 0
    assert result["missing_keys"] == 0


def test_parquet_round_trip_preserves_frl_relationships() -> None:
    result = run_relationship_proof(
        fixture_stats=DEFAULT_FIXTURE_SOURCE,
        fixture_master=DEFAULT_FIXTURE_MASTER,
        identity_registry=DEFAULT_IDENTITY_REGISTRY,
        team_registry=DEFAULT_TEAM_REGISTRY,
        player_source=DEFAULT_PLAYER_SOURCE,
    )
    assert result["fixture_stat_orphans"] == 0
    assert result["home_team_orphans"] == 0
    assert result["away_team_orphans"] == 0
    assert result["identity_verified_rows"] > 0
    assert result["player_records_with_verified_identity"] > 0
    assert result["verified_identity_orphans"] == 0
