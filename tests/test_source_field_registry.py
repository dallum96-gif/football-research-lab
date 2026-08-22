from source_field_registry import field_inventory, fields_for_family


def test_all_required_source_families_are_registered():
    inventory = field_inventory()
    assert {"team_match", "player_match", "player_season", "squad"}.issubset(inventory)


def test_registry_preserves_source_native_naming():
    player_fields = {spec.source_field for spec in fields_for_family("player_match")}
    team_fields = {spec.source_field for spec in fields_for_family("team_match")}

    assert "progressiveBallCarriesCount" in player_fields
    assert "expectedGoals" in player_fields
    assert "possessionPercentage" in team_fields
    assert "ground" in team_fields


def test_first_player_season_promotion_batch_is_exposed():
    fields = {spec.source_field: spec for spec in fields_for_family("player_season")}
    promoted = {
        "aerialDuels",
        "aerialDuelsLost",
        "aerialDuelsWon",
        "blockedShots",
        "expectedGoalsFreekick",
        "expectedGoalsOnTarget",
        "expectedGoalsOnTargetConceded",
        "shotsBlockedInBox",
        "shotsBlockedOutsideBox",
        "shotsOnTargetIncGoals",
    }
    assert promoted.issubset(fields)
    assert all(fields[name].semantic_status == "exposed" for name in promoted)


def test_registry_status_is_not_a_ui_decision():
    allowed = {"retained", "exposed", "derived", "restricted", "unknown"}
    for family in field_inventory():
        for spec in fields_for_family(family):
            assert spec.semantic_status in allowed
