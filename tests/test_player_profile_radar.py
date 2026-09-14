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
        "progressive_carries_per_90",
        "recoveries_per_90",
        "tackles_won_per_90",
    } == set(keys)


def test_historical_odegaard_profile_uses_progressive_carrying() -> None:
    from player_profile_radar import build_player_profile_radar

    result = build_player_profile_radar("2025-26", "184029")

    assert result is not None
    assert result["available"] is True
    assert len(result["axes"]) == 6

    carrying = next(
        axis
        for axis in result["axes"]
        if axis["label"] == "Carrying"
    )

    assert carrying["key"] == "progressive_carries_per_90"
    assert carrying["value"] is not None
    assert carrying["availability"] in {"AVAILABLE", "PARTIAL"}


def test_current_odegaard_profile_preserves_missing_carrying() -> None:
    from player_profile_radar import build_player_profile_radar

    result = build_player_profile_radar("2026-27", "184029")

    assert result is not None
    assert result["available"] is True
    assert result["complete"] is False
    assert len(result["axes"]) == 6

    carrying = next(
        axis
        for axis in result["axes"]
        if axis["label"] == "Carrying"
    )

    assert carrying["key"] == "progressive_carries_per_90"
    assert carrying["availability"] == "UNAVAILABLE"
    assert carrying["value"] is None
    assert carrying["percentile"] is None
