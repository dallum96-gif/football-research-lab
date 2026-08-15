import os
import sys

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, ROOT)

import player_research


def test_multi_season_totals():
    players = (
        player_research.multi_season_players(
            "2021-22",
            "2025-26",
        )
    )

    haaland = next(
        player
        for player in players
        if player["canonical_name"]
        == "erling haaland"
    )

    assert haaland["season_count"] == 5
    assert haaland["goals"] > 27
    assert haaland["minutes"] > 0
    assert haaland["xg"] > 0


def test_multi_season_per_90():
    players = (
        player_research.multi_season_players(
            "2021-22",
            "2025-26",
        )
    )

    haaland = next(
        player
        for player in players
        if player["canonical_name"]
        == "erling haaland"
    )

    expected = (
        haaland["goals"]
        / haaland["minutes"]
        * 90
    )

    assert abs(
        haaland["goals_per_90"]
        - expected
    ) < 1e-12


def test_cross_season_identity():
    players = (
        player_research.multi_season_players(
            "2021-22",
            "2025-26",
        )
    )

    haaland = next(
        player
        for player in players
        if player["canonical_name"]
        == "erling haaland"
    )

    assert haaland["season_count"] == 5

    assert set(
        haaland["seasons"]
    ) == {
        "2021-22",
        "2022-23",
        "2023-24",
        "2024-25",
        "2025-26",
    }


def test_filter_conditions():
    players = (
        player_research.multi_season_players(
            "2021-22",
            "2025-26",
        )
    )

    filtered = (
        player_research.filter_players(
            players,
            min_minutes=1000,
            min_seasons=3,
            filters=[
                (
                    "goals",
                    "At least",
                    20,
                ),
                (
                    "xg_per_90",
                    "At least",
                    0.20,
                ),
            ],
        )
    )

    assert filtered

    assert all(
        player["minutes"] >= 1000
        and player["season_count"] >= 3
        and player["goals"] >= 20
        and player["xg_per_90"] >= 0.20
        for player in filtered
    )


def test_name_search_identity():
    players = (
        player_research.multi_season_players(
            "2021-22",
            "2025-26",
        )
    )

    matches = [
        player
        for player in players
        if "haaland"
        in player["player_name"].casefold()
    ]

    assert len(matches) == 1
    assert (
        matches[0]["player_name"]
        == "Erling Haaland"
    )


def test_multi_season_club_history():
    players = (
        player_research.multi_season_players(
            "2021-22",
            "2025-26",
        )
    )

    haaland = next(
        player
        for player in players
        if player["canonical_name"]
        == "erling haaland"
    )

    assert haaland["clubs"]
    assert any(
        "Man City"
        in club
        for club in haaland["clubs"]
    )


TESTS = [
    test_multi_season_totals,
    test_multi_season_per_90,
    test_cross_season_identity,
    test_filter_conditions,
    test_name_search_identity,
    test_multi_season_club_history,
]


if __name__ == "__main__":
    passed = 0

    for test in TESTS:
        try:
            test()
            print(
                f"PASS  {test.__name__}"
            )
            passed += 1
        except Exception as exc:
            print(
                f"FAIL  {test.__name__}: {exc}"
            )

    print()
    print(
        f"PLAYER RESEARCH V0.2: "
        f"{passed}/{len(TESTS)}"
    )

    if passed != len(TESTS):
        raise SystemExit(1)
