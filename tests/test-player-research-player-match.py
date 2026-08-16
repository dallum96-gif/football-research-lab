import player_research_player_match


def test_module_shape():
    assert hasattr(player_research_player_match, "enrich_aggregate")
    assert hasattr(player_research_player_match, "enrich_players")


def test_fail_closed_unresolved():
    player = {"_records": [{"_season": "2020-21", "element": "999999"}]}
    enriched = player_research_player_match.enrich_aggregate(player)
    assert enriched["player_match_identity_status"] == "UNAVAILABLE"
    assert enriched["player_match_source_player_id"] is None
    assert enriched["player_match_identity_reason"] == "NO_VERIFIED_SOURCE_ID"


if __name__ == "__main__":
    tests = [test_module_shape, test_fail_closed_unresolved]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"PLAYER RESEARCH PLAYER-MATCH TESTS: {len(tests)}/{len(tests)}")
