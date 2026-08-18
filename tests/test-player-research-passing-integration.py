import player_research
import player_research_player_match
import player_match_research


def test_player_match_passing_overrides():
    original = player_match_research.player_match_evidence_for_records
    player_match_research.player_match_evidence_for_records = lambda rows: {
        "status": "VERIFIED",
        "reason": "TEST_VERIFIED",
        "source_player_id": "934235",
        "metrics": {
            "passes": 100,
            "accurate_passes": 88,
            "key_passes": 7,
            "big_chances_created": 2,
        },
    }
    try:
        player = {
            "player_name": "Test Player",
            "attempted_passes": 1,
            "completed_passes": 1,
            "key_passes": 1,
            "big_chances_created": 1,
            "creativity": 10,
            "_records": ({"_season": "2025-26", "element": "999"},),
        }
        enriched = player_research_player_match.enrich_aggregate(player)
        assert enriched["player_match_identity_status"] == "VERIFIED"
        assert enriched["player_match_source_player_id"] == "934235"
        assert enriched["player_match_passes"] == 100
        assert enriched["player_match_accurate_passes"] == 88
        assert enriched["player_match_key_passes"] == 7
        assert enriched["player_match_big_chances_created"] == 2
        assert enriched["creativity"] == 10
    finally:
        player_match_research.player_match_evidence_for_records = original


def test_unresolved_is_fail_closed():
    original = player_match_research.player_match_evidence_for_records
    player_match_research.player_match_evidence_for_records = lambda rows: {
        "status": "UNAVAILABLE",
        "reason": "NO_VERIFIED_SOURCE_ID",
        "source_player_id": None,
        "metrics": {},
    }
    try:
        player = {
            "player_name": "Unresolved Player",
            "attempted_passes": 1,
            "completed_passes": 1,
            "key_passes": 1,
            "big_chances_created": 1,
            "_records": ({"_season": "2025-26", "element": "not-verified"},),
        }
        enriched = player_research_player_match.enrich_aggregate(player)
        assert enriched["player_match_identity_status"] == "UNAVAILABLE"
        assert enriched["player_match_source_player_id"] is None
        assert "player_match_passes" not in enriched
        assert "player_match_accurate_passes" not in enriched
    finally:
        player_match_research.player_match_evidence_for_records = original


def test_existing_player_research_contract_is_untouched():
    assert hasattr(player_research, "_aggregate")
    assert callable(player_research._aggregate)


if __name__ == "__main__":
    tests = [
        test_player_match_passing_overrides,
        test_unresolved_is_fail_closed,
        test_existing_player_research_contract_is_untouched,
    ]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"PLAYER RESEARCH PASSING INTEGRATION TESTS: {len(tests)}/{len(tests)}")
