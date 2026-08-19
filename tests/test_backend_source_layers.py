from pathlib import Path

import build_player_season_evidence as player_season
import build_squad_evidence as squad
import build_fpl_player_gw_evidence as fpl_gw
import build_fpl_fixture_evidence as fpl_fixture

SEASON = "2016-17"

def test_player_season_source_files():
    paths = player_season.source_files(SEASON)
    assert paths
    assert all(not any(part.startswith("_") for part in p.parts) for p in paths)
    assert all(p.parent.name == "players_stats" for p in paths)


def test_squad_source_files():
    paths = squad.source_files(SEASON)
    assert paths
    assert all(not any(part.startswith("_") for part in p.parts) for p in paths)
    assert all(p.parent.name == "squad" for p in paths)


def test_fpl_sources():
    assert fpl_gw.source_file(SEASON).name == "2016-17_all_players_gw.csv"
    assert fpl_fixture.UPSTREAM_ROOT.name == "fpl_stats"


TESTS = [
    test_player_season_source_files,
    test_squad_source_files,
    test_fpl_sources,
]

if __name__ == "__main__":
    passed = 0
    for test in TESTS:
        try:
            test()
            print(f"PASS  {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL  {test.__name__}: {exc}")
    print()
    print(f"BACKEND SOURCE-LAYER TESTS: {passed}/{len(TESTS)}")
    if passed != len(TESTS):
        raise SystemExit(1)
