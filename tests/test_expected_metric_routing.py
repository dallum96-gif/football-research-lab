import pytest

from expected_metric_routing import (
    COMPLETE,
    COVERAGE_GAP,
    DIRECT_TEAM_MATCH,
    EXPECTED_ASSISTS,
    EXPECTED_GOALS,
    EXPECTED_GOALS_ON_TARGET,
    NEAR_COMPLETE,
    NO_GOVERNED_SEASON_ROUTE,
    PARTIAL,
    PLAYER_MATCH_DERIVED_TEAM_MATCH,
    cross_season_route,
    single_season_route,
)


def test_pre_2022_expected_metric_fragments_do_not_become_season_route():
    route = single_season_route(EXPECTED_GOALS, "2020-21")

    assert route.representation == NO_GOVERNED_SEASON_ROUTE
    assert route.coverage_status == COVERAGE_GAP
    assert route.observed_fixtures == 5
    assert route.representation_mixing_allowed is False


def test_xg_2024_25_prefers_complete_player_derived_route():
    route = single_season_route(EXPECTED_GOALS, "2024-25")

    assert route.representation == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert route.observed_fixtures == 380
    assert route.eligible_fixtures == 380
    assert route.coverage_status == COMPLETE


def test_xg_2023_24_exposes_residual_player_route_gap():
    route = single_season_route(EXPECTED_GOALS, "2023-24")

    assert route.representation == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert route.observed_fixtures == 379
    assert route.coverage_status == NEAR_COMPLETE


def test_complete_2025_26_direct_xg_is_preferred_for_single_season_view():
    route = single_season_route(EXPECTED_GOALS, "2025-26")

    assert route.representation == DIRECT_TEAM_MATCH
    assert route.coverage_status == COMPLETE
    assert route.representation_mixing_allowed is False


def test_xa_player_route_is_complete_for_2022_23_through_2024_25():
    for season in ("2022-23", "2023-24", "2024-25"):
        route = single_season_route(EXPECTED_ASSISTS, season)
        assert route.representation == PLAYER_MATCH_DERIVED_TEAM_MATCH
        assert route.coverage_status == COMPLETE
        assert route.observed_fixtures == 380


def test_xgot_prefers_player_route_when_it_is_stronger_but_keeps_partial_status():
    route = single_season_route(EXPECTED_GOALS_ON_TARGET, "2024-25")

    assert route.representation == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert route.observed_fixtures == 334
    assert route.coverage_status == PARTIAL


def test_xgot_2025_26_prefers_near_complete_direct_route():
    route = single_season_route(EXPECTED_GOALS_ON_TARGET, "2025-26")

    assert route.representation == DIRECT_TEAM_MATCH
    assert route.observed_fixtures == 379
    assert route.coverage_status == NEAR_COMPLETE


def test_cross_season_xg_uses_one_consistent_player_derived_representation():
    route = cross_season_route(
        EXPECTED_GOALS,
        ("2022-23", "2023-24", "2024-25", "2025-26"),
    )

    assert route.representation == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert route.observed_fixtures == 1519
    assert route.eligible_fixtures == 1520
    assert route.coverage_status == NEAR_COMPLETE
    assert route.representation_mixing_allowed is False


def test_cross_season_xa_is_complete_under_consistent_player_derived_route():
    route = cross_season_route(
        EXPECTED_ASSISTS,
        ("2022-23", "2023-24", "2024-25", "2025-26"),
    )

    assert route.representation == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert route.observed_fixtures == 1520
    assert route.coverage_status == COMPLETE


def test_cross_season_xgot_exposes_material_partial_coverage():
    route = cross_season_route(
        EXPECTED_GOALS_ON_TARGET,
        ("2022-23", "2023-24", "2024-25", "2025-26"),
    )

    assert route.representation == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert route.observed_fixtures == 1365
    assert route.eligible_fixtures == 1520
    assert route.coverage_status == PARTIAL


def test_cross_season_route_fails_closed_when_period_crosses_pre_2022_gap():
    route = cross_season_route(
        EXPECTED_GOALS,
        ("2021-22", "2022-23", "2023-24"),
    )

    assert route.representation == NO_GOVERNED_SEASON_ROUTE
    assert route.coverage_status == COVERAGE_GAP
    assert route.representation_mixing_allowed is False


def test_unaudited_future_season_is_rejected():
    with pytest.raises(ValueError, match="not governed"):
        single_season_route(EXPECTED_GOALS, "2026-27")


def test_unknown_expected_metric_is_rejected():
    with pytest.raises(ValueError, match="Unsupported expected metric"):
        single_season_route("Expected possession", "2025-26")
