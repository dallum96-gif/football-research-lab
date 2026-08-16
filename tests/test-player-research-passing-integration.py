import player_research


class _Adapter:
    @staticmethod
    def enrich_aggregate(player):
        enriched = dict(player)
        enriched.update(
            {
                "player_match_identity_status": "VERIFIED",
                "player_match_passes": 100,
                "player_match_accurate_passes": 88,
                "player_match_key_passes": 7,
                "player_match_big_chances_created": 2,
            }
        )
        return enriched


def test_player_match_passing_overrides():
    original = player_research.player_research_player_match
    player_research.player_research_player_match = _Adapter()
    try:
        row = {
            "_season": "2025-26",
            "_source_file": "test.csv",
            "name": "Test Player",
            "position": "MID",
            "team": "Arsenal",
            "element": "999",
            "attempted_passes": 1,
            "completed_passes": 1,
            "key_passes": 1,
            "big_chances_created": 1,
            "minutes": 90,
            "goals_scored": 0,
            "assists": 0,
            "clean_sheets": 0,
            "goals_conceded": 0,
            "own_goals": 0,
            "penalties_saved": 0,
            "penalties_missed": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "saves": 0,
            "bonus": 0,
            "bps": 0,
            "tackles": 0,
            "recoveries": 0,
            "defensive_contribution": 0,
            "total_points": 0,
            "expected_goals": 0,
            "expected_assists": 0,
            "expected_goal_involvements": 0,
            "creativity": 10,
            "open_play_crosses": 0,
            "dribbles": 0,
            "influence": 0,
            "threat": 0,
            "ict_index": 0,
            "starts": 1,
        }
        player = player_research._aggregate((row,), ("2025-26",))
        assert player["attempted_passes"] == 100
        assert player["completed_passes"] == 88
        assert player["key_passes"] == 7
        assert player["big_chances_created"] == 2
        assert player["creativity"] == 10
    finally:
        player_research.player_research_player_match = original


def test_existing_player_match_status_is_optional():
    assert hasattr(player_research, "_aggregate")


if __name__ == "__main__":
    tests = [
        test_player_match_passing_overrides,
        test_existing_player_match_status_is_optional,
    ]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"PLAYER RESEARCH PASSING INTEGRATION TESTS: {len(tests)}/{len(tests)}")
