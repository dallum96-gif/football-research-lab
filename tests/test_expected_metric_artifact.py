from expected_metric_artifact import (
    artifact_metadata,
    fixture_expected_metric_row,
    team_expected_metric_observation,
)
from expected_metric_routing import (
    EXPECTED_ASSISTS,
    EXPECTED_GOALS,
    PLAYER_MATCH_DERIVED_TEAM_MATCH,
)


def test_artifact_metadata_is_pinned_and_governed():
    metadata = artifact_metadata()

    assert metadata["representation"] == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert metadata["metric"] == EXPECTED_GOALS
    assert metadata["construction_version"] == "FRL_PLAYER_DERIVED_EXPECTED_METRICS_V1"
    assert metadata["source_commit"] == "1ec7f0dc79055902251cd938650f622b0e79f3cc"
    assert metadata["representation_mixing_allowed"] is False
    assert metadata["coverage_fixtures"] == {
        "2022-23": 380,
        "2023-24": 379,
        "2024-25": 380,
        "2025-26": 380,
    }


def test_fixture_lookup_uses_canonical_fixture_index():
    row = fixture_expected_metric_row("2022-23", "1")

    assert row == {
        "season": "2022-23",
        "fixture_id": "1",
        "representation": PLAYER_MATCH_DERIVED_TEAM_MATCH,
        "home_expected_goals": 1.2118,
        "away_expected_goals": 0.9968,
    }


def test_available_player_derived_xg_preserves_governed_provenance():
    observation = team_expected_metric_observation(
        "2022-23",
        "1",
        "home",
        EXPECTED_GOALS,
    )

    assert observation["status"] == "AVAILABLE"
    assert observation["value"] == 1.2118
    assert observation["representation"] == PLAYER_MATCH_DERIVED_TEAM_MATCH
    assert observation["construction_version"] == "FRL_PLAYER_DERIVED_EXPECTED_METRICS_V1"
    assert observation["source_commit"] == "1ec7f0dc79055902251cd938650f622b0e79f3cc"


def test_positive_trigger_xg_gap_fails_closed():
    observation = team_expected_metric_observation(
        "2023-24",
        "45",
        "home",
        EXPECTED_GOALS,
    )

    assert observation["status"] == "MISSING_POSITIVE_TRIGGER_INPUT"
    assert observation["value"] is None
    assert observation["reason"] == "PLAYER_XG_MISSING_WITH_POSITIVE_SHOT_TRIGGER"


def test_governed_xa_is_not_falsely_presented_as_product_packaged():
    observation = team_expected_metric_observation(
        "2024-25",
        "1",
        "home",
        EXPECTED_ASSISTS,
    )

    assert observation["status"] == "UNAVAILABLE"
    assert observation["value"] is None
    assert observation["reason"] == "GOVERNED_BUT_NOT_PRODUCT_PACKAGED"


def test_outside_materialized_period_is_unavailable_not_fabricated():
    observation = team_expected_metric_observation(
        "2021-22",
        "1",
        "home",
        EXPECTED_GOALS,
    )

    assert observation["status"] == "UNAVAILABLE"
    assert observation["value"] is None
    assert observation["reason"] == "FIXTURE_OUTSIDE_MATERIALIZED_ARTIFACT"


def test_artifact_hash_is_platform_newline_neutral():
    """Tracked artifact integrity must not depend on LF versus CRLF checkout."""
    metadata = artifact_metadata()
    assert metadata["season_file_sha256"]["2022-23"] == "cd2bba6bb9589a9999d920a570e156c1dda9b9e598ba459c4d25f5a53013fe8f"
