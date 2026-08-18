import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, ROOT)

import query_lab
import player_research


def test_player_aggregation():
    players = player_research.season_players(
        "2025-26"
    )

    haaland = next(
        player
        for player in players
        if player["player_name"]
        == "Erling Haaland"
    )

    rows, _, _ = query_lab.load_player_rows(
        "2025-26"
    )

    source_rows = [
        row
        for row in rows
        if str(row["player_code"])
        == str(haaland["player_code"])
    ]

    assert haaland["goals"] == sum(
        query_lab.to_number(
            row["goals_scored"]
        )
        for row in source_rows
    )

    assert haaland["minutes"] == sum(
        query_lab.to_number(
            row["minutes"]
        )
        for row in source_rows
    )

    assert haaland["xg"] == sum(
        query_lab.to_number(
            row["expected_goals"]
        )
        for row in source_rows
    )

    assert haaland["xa"] == sum(
        query_lab.to_number(
            row["expected_assists"]
        )
        for row in source_rows
    )


def test_per_90():
    player = next(
        player
        for player
        in player_research.season_players(
            "2025-26"
        )
        if player["player_name"]
        == "Erling Haaland"
    )

    expected = (
        player["goals"]
        / player["minutes"]
        * 90
    )

    assert abs(
        player["goals_per_90"] - expected
    ) < 1e-12


def test_player_identity():
    rows, _, _ = query_lab.load_player_rows(
        "2025-26"
    )

    identities = defaultdict(set)

    for row in rows:
        code = row.get("player_code")

        identities[code].add(
            (
                row.get("first_name", ""),
                row.get("second_name", ""),
            )
        )

    conflicts = {
        code: names
        for code, names in identities.items()
        if code and len(names) > 1
    }

    assert conflicts == {}


def test_player_team_bridge():
    identity_rows = (
        query_lab.load_identity_registry()
    )

    verified = {
        (
            "2025-26",
            str(row["persistent_team_code"]),
        )
        for row in identity_rows
        if (
            row["season"] == "2025-26"
            and row["mapping_status"] == "VERIFIED"
        )
    }

    rows, _, _ = query_lab.load_player_rows(
        "2025-26"
    )

    player_codes = {
        (
            "2025-26",
            str(row["team_code"]),
        )
        for row in rows
        if row.get("team_code")
    }

    assert player_codes <= verified


def test_player_filters():
    players = player_research.season_players(
        "2025-26"
    )

    filtered = player_research.filter_players(
        players,
        min_minutes=1000,
        filters=[
            (
                "goals",
                "At least",
                10,
            ),
            (
                "xg_per_90",
                "At least",
                0.25,
            ),
        ],
    )

    assert filtered

    assert all(
        player["minutes"] >= 1000
        and player["goals"] >= 10
        and player["xg_per_90"] >= 0.25
        for player in filtered
    )


def test_player_provenance():
    player = player_research.player_detail(
        "2025-26",
        "223094",
    )

    assert player is not None

    evidence = player["_evidence"]

    assert (
        evidence["query_version"]
        == query_lab.QUERY_VERSION
    )

    assert evidence["season"] == "2025-26"

    assert evidence["source_file"].endswith(
        "2025-26_all_players_gw.csv"
    )

    assert evidence["source_rows"] > 0

    assert (
        evidence["aggregation"]
        != ""
    )


TESTS = [
    test_player_aggregation,
    test_per_90,
    test_player_identity,
    test_player_team_bridge,
    test_player_filters,
    test_player_provenance,
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
        f"PLAYER RESEARCH TESTS: "
        f"{passed}/{len(TESTS)}"
    )

    if passed != len(TESTS):
        raise SystemExit(1)
