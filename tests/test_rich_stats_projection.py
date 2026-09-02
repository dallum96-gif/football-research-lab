from __future__ import annotations

import match_stats
import rich_player_projection


def test_rich_team_source_map_contains_promoted_vocabulary() -> None:
    expected = {
        "Final third entries": "finalThirdEntries",
        "Penalty area entries": "penAreaEntries",
        "Touches in opposition box": "touchesInOppBox",
        "Forward passes": "fwdPass",
        "Long balls": "totalLongBalls",
        "Accurate long balls": "accurateLongBalls",
        "Duels won": "duelWon",
        "Aerial duels won": "aerialWon",
        "Possession won attacking third": "possWonAtt3rd",
        "Shots inside box": "attemptsIbox",
        "Shots conceded inside box": "attemptsConcededIbox",
        "Errors leading to shot": "errorLeadToShot",
        "Saves inside box": "savedIbox",
        "Keeper sweeper actions": "totalKeeperSweeper",
    }
    for label, source_field in expected.items():
        assert match_stats.CORE_FIELDS[label] == source_field


def test_xgot_positive_shot_on_target_blank_fails_closed() -> None:
    records = (
        {"expectedGoalsOnTarget": "0.4", "onTargetScoringAttempt": "1"},
        {"expectedGoalsOnTarget": "", "onTargetScoringAttempt": "1"},
    )
    fields = {"expectedGoalsOnTarget", "onTargetScoringAttempt"}

    result = rich_player_projection.aggregate_source_records(records, fields)

    assert result["xgot"] is None


def test_xgot_structural_zero_does_not_inflate_observed_total() -> None:
    records = (
        {"expectedGoalsOnTarget": "0.4", "onTargetScoringAttempt": "1"},
        {"expectedGoalsOnTarget": "", "onTargetScoringAttempt": "0"},
    )
    fields = {"expectedGoalsOnTarget", "onTargetScoringAttempt"}

    result = rich_player_projection.aggregate_source_records(records, fields)

    assert result["xgot"] == 0.4


def test_absent_rich_source_field_stays_unavailable() -> None:
    records = ({"totalShots": "3"},)

    result = rich_player_projection.aggregate_source_records(records, {"totalShots"})

    assert result["shots"] == 3.0
    assert result["progressive_carries"] is None


def test_missing_packaged_player_projection_degrades_to_unavailable(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(rich_player_projection, "PACKAGED", tmp_path / "missing.csv")
    rich_player_projection.clear_caches()
    try:
        player = {"player_code": "123", "goals": 4}
        enriched = rich_player_projection.enrich_player(player, "2025-26")

        assert enriched["goals"] == 4
        assert enriched["shots"] is None
        assert enriched["xgot"] is None
        assert enriched["_rich_player_projection"] == "UNAVAILABLE"
    finally:
        rich_player_projection.clear_caches()
