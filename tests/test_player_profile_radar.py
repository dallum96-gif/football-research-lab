from player_profile_radar import MIDFIELD_PROFILE_TEMPLATE


def test_midfield_profile_template_is_unique_and_balanced():
    keys = [
        key
        for key, _label
        in MIDFIELD_PROFILE_TEMPLATE
    ]

    labels = [
        label
        for _key, label
        in MIDFIELD_PROFILE_TEMPLATE
    ]

    assert len(keys) == 6
    assert len(set(keys)) == 6
    assert len(set(labels)) == 6

    assert {
        "xg_per_90",
        "xa_per_90",
        "accurate_opposition_half_passes_per_90",
        "forward_passes_per_90",
        "recoveries_per_90",
        "tackles_won_per_90",
    } == set(keys)


def test_historical_odegaard_profile_uses_source_native_forward_passing() -> None:
    from player_profile_radar import build_player_profile_radar

    result = build_player_profile_radar("2025-26", "184029")

    assert result is not None
    assert result["available"] is True
    assert len(result["axes"]) == 6

    forward_passing = next(
        axis
        for axis in result["axes"]
        if axis["label"] == "Forward passing"
    )

    assert forward_passing["key"] == "forward_passes_per_90"
    assert abs(forward_passing["value"] - (264 / 1363 * 90)) < 1e-9
    assert forward_passing["availability"] == "PARTIAL"


def test_odegaard_pre_player_code_profile_uses_verified_historical_identity() -> None:
    from player_profile_radar import build_player_profile_radar

    result = build_player_profile_radar("2024-25", "13")

    assert result is not None
    forward_passing = next(
        axis
        for axis in result["axes"]
        if axis["label"] == "Forward passing"
    )

    assert abs(forward_passing["value"] - (445 / 2321 * 90)) < 1e-9
    assert forward_passing["availability"] == "PARTIAL"


def test_current_odegaard_profile_has_complete_forward_passing_comparison() -> None:
    from player_profile_radar import build_player_profile_radar

    result = build_player_profile_radar("2026-27", "184029")

    assert result is not None
    assert result["available"] is True
    assert result["complete"] is True
    assert len(result["axes"]) == 6

    forward_passing = next(
        axis
        for axis in result["axes"]
        if axis["label"] == "Forward passing"
    )

    assert forward_passing["key"] == "forward_passes_per_90"
    assert abs(forward_passing["value"] - (45 / 221 * 90)) < 1e-9
    assert forward_passing["availability"] == "AVAILABLE"
    assert forward_passing["observed_players"] == 108
    assert forward_passing["eligible_players"] == 108
    assert forward_passing["percentile"] is not None
