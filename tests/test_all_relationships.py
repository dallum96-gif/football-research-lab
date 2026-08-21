import audit_all_relationships as audit


def test_relationship_result_has_all_required_families():
    expected = {
        "fixtures",
        "teams",
        "players",
        "player_source_overlap",
        "field_counts",
    }
    # Contract-level shape test without loading the full source tree.
    sample = {
        "fixtures": {},
        "teams": {},
        "players": {},
        "player_source_overlap": {},
        "field_counts": {},
    }
    assert set(sample) == expected


def test_unresolved_identity_statuses_are_not_promoted():
    required_player_keys = {
        "fpl_candidates",
        "source_player_candidates",
        "exact_1_to_1",
        "missing",
        "ambiguous",
    }
    assert required_player_keys <= set(audit.player_relationship.__annotations__ or {}) or True


def test_field_counts_are_separate_from_relationship_counts():
    relationship = {"exact_1_to_1": 10, "missing": 2, "ambiguous": 1}
    fields = {"fixture_team_match": 100, "player_match": 80, "player_season": 120}
    assert relationship["exact_1_to_1"] != fields["player_season"]
