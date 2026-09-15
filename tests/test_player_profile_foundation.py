from __future__ import annotations

import player_profile_foundation


def test_current_odegaard_profile_uses_one_player_season_representation() -> None:
    result = player_profile_foundation.build_player_profile("2026-27", "184029")

    assert result is not None
    assert result["milestone"] == "PLAYER_PROFILE_UNIVERSAL_FOUNDATION_V1"
    profile = result["profile"]
    assert profile["player_identity_key"] == "player_match:547410"
    assert profile["portrait_player_code"] == "184029"
    assert profile["primary_club"] == "Arsenal"
    assert profile["appearances"] == 3
    assert profile["starts"] == 3
    assert profile["minutes"] == 224
    assert profile["participation_representation"] == "PLAYER_PROFILE_SOURCE_STATS_V1"

    comparison = result["comparison"]
    assert comparison["available"] is True
    assert comparison["source_representation"] == "PLAYER_PROFILE_SOURCE_STATS_V1"
    assert comparison["denominator_representation"] == "Player-Season timePlayed"
    assert len(comparison["axes"]) == 6
    assert all(axis["denominator"] == "timePlayed" for axis in comparison["axes"])

    forward = next(axis for axis in comparison["axes"] if axis["key"] == "forward_passes_per_90")
    assert abs(forward["value"] - (45 / 224 * 90)) < 1e-9


def test_current_odegaard_biography_is_packaged() -> None:
    result = player_profile_foundation.build_player_profile("2026-27", "184029")
    assert result is not None
    biography = result["profile"]["biography"]
    assert biography["available"] is True
    assert biography["nationality"] == "Norway"
    assert biography["evidence"]["runtime_source"] == "data/player_profile_biography_v1.csv"


def test_non_midfielder_keeps_universal_profile_but_not_mid_radar() -> None:
    result = player_profile_foundation.build_player_profile("2026-27", "226597")
    assert result is not None
    assert result["profile"]["player_name"].startswith("Gabriel")
    assert result["profile"]["biography"]["available"] is True
    assert result["profile"]["biography"]["nationality"] == "Brazil"
    assert result["comparison"]["available"] is False
    assert "only for MID" in result["comparison"]["limitations"][0]


def test_goalkeeper_profile_keeps_packaged_biography_without_mid_radar() -> None:
    result = player_profile_foundation.build_player_profile("2026-27", "154561")
    assert result is not None
    assert result["profile"]["player_name"].startswith("David Raya")
    assert result["profile"]["biography"]["available"] is True
    assert result["profile"]["biography"]["nationality"] == "Spain"
    assert result["comparison"]["available"] is False


def test_low_minute_midfielder_fails_profile_threshold_without_becoming_zero() -> None:
    result = player_profile_foundation.build_player_profile("2026-27", "232413")
    assert result is not None
    assert result["profile"]["position"] == "MID"
    assert result["comparison"]["available"] is False
    assert "does not meet" in result["comparison"]["limitations"][0]
