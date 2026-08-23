from source_field_taxonomy import CATEGORIES, build_taxonomy, classify_field


def test_every_uncatalogued_field_gets_one_primary_category():
    rows = build_taxonomy()
    assert len(rows) == 325
    assert all(row.primary_category in CATEGORIES for row in rows)
    assert len({(row.family, row.source_field) for row in rows}) == 325


def test_taxonomy_does_not_change_registry_status():
    rows = build_taxonomy()
    assert all(row.registry_status == "UNCATALOGUED" for row in rows)


def test_representative_navigation_categories():
    assert classify_field("player_season", "goals")[0] == "Shooting & Finishing"
    assert classify_field("player_season", "duelsWon")[0] == "Duels & Aerials"
    assert classify_field("player_season", "successfulLongPasses")[0] == "Passing & Distribution"
    assert classify_field("player_season", "successfulDribbles")[0] == "Dribbling & Carrying"
    assert classify_field("player_match", "yellowCards")[0] == "Discipline"
    assert classify_field("player_match", "saves")[0] == "Goalkeeping"


def test_explicit_unclassified_exceptions_are_placed():
    assert classify_field("player_match", "penaltyConceded")[0] == "Discipline"
    assert classify_field("player_match", "penaltyFaced")[0] == "Discipline"
    assert classify_field("player_match", "penaltyMiss")[0] == "Shooting & Finishing"
    assert classify_field("player_match", "penaltyWon")[0] == "Chance Creation"
    assert classify_field("player_match", "substitute.1")[0] == "Playing Time"
