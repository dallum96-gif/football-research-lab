from profile_variable_dictionary import profile


def test_profile_counts_all_rows():
    rows = [
        {"grain": "player_match", "resource": "player_match", "navigation_category": "Shooting & Finishing", "semantic_status": "VERIFIED", "source_surface": "FRL_LOCAL_CSV"},
        {"grain": "team_match", "resource": "team_match", "navigation_category": "Crossing & Set Pieces", "semantic_status": "UNCATALOGUED", "source_surface": "FRL_LOCAL_CSV"},
    ]
    p = profile(rows)
    assert sum(p["grain"].values()) == 2
    assert p["grain"]["player_match"] == 1
    assert p["category"]["Crossing & Set Pieces"] == 1


def test_profile_preserves_distinct_grains():
    rows = [
        {"grain": "player_match", "resource": "r", "navigation_category": "Shooting & Finishing", "semantic_status": "", "source_surface": "x"},
        {"grain": "team_match", "resource": "r", "navigation_category": "Shooting & Finishing", "semantic_status": "", "source_surface": "x"},
    ]
    p = profile(rows)
    assert p["grain"]["player_match"] == 1
    assert p["grain"]["team_match"] == 1
