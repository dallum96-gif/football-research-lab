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
        "successful_dribbles_per_90",
        "recoveries_per_90",
        "tackles_won_per_90",
    } == set(keys)
