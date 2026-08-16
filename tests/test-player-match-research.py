import player_match_research


def test_module_shape():
    assert hasattr(player_match_research, "load_registry")
    assert hasattr(player_match_research, "source_player_id_for_record")
    assert hasattr(player_match_research, "enrich_player")


def test_unknown_record_is_unavailable():
    row = {"_season": "2020-21", "element": "999999"}
    assert player_match_research.source_player_id_for_record(row) is None


def test_enrichment_is_fail_closed_without_registry():
    player_match_research.load_registry.cache_clear()
    player = {"_records": [{"_season": "2020-21", "element": "999999"}]}
    enriched = player_match_research.enrich_player(player)
    assert enriched["player_match_identity_status"] == "UNAVAILABLE"
    assert enriched["player_match_source_player_id"] is None


if __name__ == "__main__":
    tests = [
        test_module_shape,
        test_unknown_record_is_unavailable,
        test_enrichment_is_fail_closed_without_registry,
    ]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"PLAYER-MATCH RESEARCH TESTS: {len(tests)}/{len(tests)}")
