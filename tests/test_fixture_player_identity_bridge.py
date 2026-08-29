from __future__ import annotations

import source_family_adapters


def _resolve(monkeypatch, rows, pulselive_player_id: str) -> dict[str, object]:
    monkeypatch.setattr(
        source_family_adapters,
        "player_match_source_rows",
        lambda season, fixture_id: tuple(rows),
    )
    source_family_adapters._fixture_pulselive_player_candidates.cache_clear()
    try:
        return source_family_adapters.resolve_pulselive_player_identity(
            "2016-17",
            "8",
            pulselive_player_id,
        )
    finally:
        source_family_adapters._fixture_pulselive_player_candidates.cache_clear()


def test_exact_pl_code_maps_to_existing_player_match_source_identity(monkeypatch) -> None:
    rows = (
        {"pl_code": "11334", "playerId": "900001"},
        {"pl_code": "11334", "playerId": "900001"},
    )

    result = _resolve(monkeypatch, rows, "11334")

    assert result["relationship_status"] == "VERIFIED"
    assert result["pulselive_source_player_id"] == "11334"
    assert result["player_match_source_player_id"] == "900001"
    assert result["player_match_source_player_id_namespace"] == "players_match_stats.playerId"
    assert result["identity_route"] == "PULSELIVE_PLAYER_ID_TO_PLAYER_MATCH_PL_CODE_TO_SOURCE_PLAYER_ID"
    assert source_family_adapters.source_player_id(rows[0]) == "900001"


def test_missing_pl_code_match_remains_unresolved(monkeypatch) -> None:
    result = _resolve(
        monkeypatch,
        ({"pl_code": "11334", "playerId": "900001"},),
        "66797",
    )

    assert result["relationship_status"] == "UNRESOLVED"
    assert result["candidate_source_player_ids"] == []
    assert result["player_match_source_player_id"] is None


def test_ambiguous_pl_code_rejects_identity_promotion(monkeypatch) -> None:
    result = _resolve(
        monkeypatch,
        (
            {"pl_code": "11334", "playerId": "900001"},
            {"pl_code": "11334", "playerId": "900002"},
        ),
        "11334",
    )

    assert result["relationship_status"] == "AMBIGUOUS"
    assert result["candidate_source_player_ids"] == ["900001", "900002"]
    assert result["player_match_source_player_id"] is None
