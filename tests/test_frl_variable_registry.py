from frl_variable_registry import model_candidates, profile_variables, stats_variables


def test_variable_universe_has_profile_and_stats_layers():
    assert profile_variables()
    assert stats_variables()


def test_model_candidates_are_temporally_bounded():
    candidates = model_candidates()
    assert candidates
    assert all(item.temporal for item in candidates)
    assert all(item.leakage_risk != "high" for item in candidates)


def test_profile_and_stats_are_not_identical():
    profile = {item.name for item in profile_variables()}
    stats = {item.name for item in stats_variables()}
    assert profile != stats
