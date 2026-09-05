from __future__ import annotations

from scripts.audit_team_match_sparse_zero_candidates import (
    evaluate_lost_corners_opponent_route,
    evaluate_player_sum_corroboration,
)


def _team_row(fixture: str, team: str, **values):
    return {
        "frl_season": "2025-26",
        "frl_fixture_id": fixture,
        "team_id": team,
        **values,
    }


def _player_row(fixture: str, team: str, **values):
    return {
        "frl_season": "2025-26",
        "frl_fixture_id": fixture,
        "team_id": team,
        **values,
    }


def test_player_sum_corroboration_can_support_structural_zero_review():
    team_rows = [
        _team_row("1", "A", blockedPass="5"),
        _team_row("2", "A", blockedPass=""),
    ]
    player_rows = [
        _player_row("1", "A", blockedPass="2"),
        _player_row("1", "A", blockedPass="3"),
        _player_row("2", "A", blockedPass="0"),
        _player_row("2", "A", blockedPass="0"),
    ]

    result = evaluate_player_sum_corroboration(
        team_rows,
        player_rows,
        "blockedPass",
        season="2025-26",
    )

    assert result["status"] == "PLAYER_MATCH_SUPPORTS_STRUCTURAL_ZERO_REVIEW"
    assert result["observed_team_player_pairs"] == 1
    assert result["observed_exact_matches"] == 1
    assert result["observed_mismatches"] == 0
    assert result["blank_team_player_zero"] == 1
    assert result["blank_team_player_positive"] == 0


def test_player_sum_corroboration_rejects_blank_when_player_sum_is_positive():
    team_rows = [_team_row("3", "A", goalKicks="")]
    player_rows = [
        _player_row("3", "A", goalKicks="1"),
        _player_row("3", "A", goalKicks="2"),
    ]

    result = evaluate_player_sum_corroboration(
        team_rows,
        player_rows,
        "goalKicks",
        season="2025-26",
    )

    assert result["status"] == "PLAYER_MATCH_CORROBORATION_REVIEW_CONFLICTS"
    assert result["blank_team_player_positive"] == 1


def test_player_blanks_do_not_become_a_fake_zero_route():
    team_rows = [_team_row("4", "A", touchesInOppBox="")]
    player_rows = [
        _player_row("4", "A", touchesInOppBox=""),
        _player_row("4", "A", touchesInOppBox=None),
    ]

    result = evaluate_player_sum_corroboration(
        team_rows,
        player_rows,
        "touchesInOppBox",
        season="2025-26",
    )

    assert result["status"] == "NO_EXACT_PLAYER_MATCH_CORROBORATION_ROUTE"
    assert result["blank_team_player_zero"] == 0
    assert result["blank_team_without_player_numeric"] == 1


def test_lost_corners_uses_opponent_within_same_season_fixture():
    rows = [
        _team_row("9", "A", lostCorners="4", cornerTaken="2"),
        _team_row("9", "B", lostCorners="2", cornerTaken="4"),
    ]

    result = evaluate_lost_corners_opponent_route(rows, season="2025-26")

    assert result["observed_pairs"] == 2
    assert result["observed_exact_matches"] == 2
    assert result["observed_mismatches"] == 0
    assert result["status"] == "OPPONENT_ROUTE_SUPPORTS_OBSERVED_EQUIVALENCE_ONLY"


def test_lost_corners_blank_positive_opponent_corner_is_a_conflict():
    rows = [
        _team_row("10", "A", lostCorners="", cornerTaken="1"),
        _team_row("10", "B", lostCorners="1", cornerTaken="3"),
    ]

    result = evaluate_lost_corners_opponent_route(rows, season="2025-26")

    assert result["blank_lostCorners_opponent_positive"] == 1
    assert result["status"] == "OPPONENT_ROUTE_REVIEW_CONFLICTS"


def test_lost_corners_blank_with_explicit_opponent_zero_supports_zero_review():
    rows = [
        _team_row("11", "A", lostCorners="", cornerTaken="2"),
        _team_row("11", "B", lostCorners="2", cornerTaken="0"),
    ]

    result = evaluate_lost_corners_opponent_route(rows, season="2025-26")

    assert result["blank_lostCorners_opponent_zero"] == 1
    assert result["observed_exact_matches"] == 1
    assert result["status"] == "OPPONENT_ROUTE_SUPPORTS_STRUCTURAL_ZERO_REVIEW"
