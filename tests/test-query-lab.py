import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))

import query_lab


def test_seasons():
    seasons = list(query_lab.season_files())

    expected = [
        "2016-17",
        "2017-18",
        "2018-19",
        "2019-20",
        "2020-21",
        "2021-22",
        "2022-23",
        "2023-24",
        "2024-25",
        "2025-26",
        "2026-27",
    ]

    assert seasons == expected


def test_top_goals():
    result = query_lab.top_players(
        "2025-26",
        "goals",
        10
    )

    assert len(result["results"]) == 10

    values = [
        item["value"]
        for item in result["results"]
    ]

    assert values == sorted(values, reverse=True)

    assert result["results"][0]["player"] == "Erling Haaland"
    assert result["results"][0]["value"] == 27


def test_player_total():
    result = query_lab.player_total(
        "2025-26",
        "Erling Haaland",
        "goals"
    )

    assert result["result"]["value"] == 27


def test_query_provenance():
    result = query_lab.top_players(
        "2025-26",
        "goals",
        10
    )

    assert result["query_version"] == "0.4.1"
    assert result["source_file"].endswith(
        "2025-26_all_players_gw.csv"
    )
    assert result["source_column"] == "goals_scored"
    assert result["source_rows"] > 0



def test_identity_registry():
    rows = query_lab.load_identity_registry()

    assert len(rows) == 220

    keys = {
        (row["season"], row["local_team_id"])
        for row in rows
    }

    assert len(keys) == 220


def test_man_city_identity():
    result = query_lab.resolve_team(
        "2019-20",
        "Man City",
    )

    assert result["persistent_team_code"] == "43"
    assert result["local_team_id"] == "11"
    assert result["mapping_status"] == "VERIFIED"


def test_bournemouth_identity():
    result = query_lab.resolve_team(
        "2025-26",
        "Bournemouth",
    )

    assert result["persistent_team_code"] == "91"
    assert result["local_team_id"] == "4"


def test_named_fixture_query():
    result = query_lab.query_fixtures(
        season="2019-20",
        team="Man City",
        limit=100,
    )

    assert result["filters"]["team_id"] == "11"
    assert (
        result["identity_resolution"]["team"][
            "persistent_team_code"
        ] == "43"
    )
    assert result["total_matches"] == 38


def test_named_opponent_query():
    result = query_lab.query_fixtures(
        season="2025-26",
        team="Man City",
        opponent="Bournemouth",
        limit=100,
    )

    assert result["filters"]["team_id"] == "13"
    assert result["filters"]["opponent_id"] == "4"
    assert result["total_matches"] == 2


def test_verified_fixture_correction():

    rows = query_lab.load_fixtures()

    matches = [
        row
        for row in rows
        if (
            row["season"] == "2019-20"
            and row["fixture_id"] == "275"
        )
    ]

    assert len(matches) == 1

    row = matches[0]

    # Corrected analytical result.
    assert row["home_score"] == "3"
    assert row["away_score"] == "0"

    # Actual match date/time.
    assert (
        row["kickoff_time"]
        == "2020-06-17T19:15:00Z"
    )

    # Original scheduled date is preserved.
    assert (
        row["scheduled_kickoff_time"]
        == "2020-03-11T19:30:00Z"
    )

    assert row["data_corrected"] == "true"
    assert (
        row["correction_status"]
        == "VERIFIED_CORRECTION"
    )
    assert (
        row["correction_source"]
        == "Premier League"
    )


def test_fixture_season_partitions():

    rows = query_lab.load_fixtures()

    expected_counts = {
        "2016-17": 380,
        "2017-18": 380,
        "2018-19": 380,
        "2019-20": 380,
        "2020-21": 380,
        "2021-22": 380,
        "2022-23": 380,
        "2023-24": 380,
        "2024-25": 380,
        "2025-26": 380,
        "2026-27": 380,
    }

    counts = {
        season: 0
        for season in expected_counts
    }

    dates = {
        season: []
        for season in expected_counts
    }

    for row in rows:

        season = row["season"]

        assert season in expected_counts

        counts[season] += 1

        dates[season].append(
            query_lab.datetime.fromisoformat(
                row["kickoff_time"].replace(
                    "Z",
                    "+00:00"
                )
            )
        )

    assert counts == expected_counts

    expected_ranges = {
        "2016-17": ("2016-08-01", "2017-06-30"),
        "2017-18": ("2017-08-01", "2018-06-30"),
        "2018-19": ("2018-08-01", "2019-06-30"),
        "2019-20": ("2019-08-01", "2020-08-31"),
        "2020-21": ("2020-08-01", "2021-08-31"),
        "2021-22": ("2021-08-01", "2022-08-31"),
        "2022-23": ("2022-08-01", "2023-08-31"),
        "2023-24": ("2023-08-01", "2024-08-31"),
        "2024-25": ("2024-08-01", "2025-08-31"),
        "2025-26": ("2025-08-01", "2026-08-31"),
        "2026-27": ("2026-08-01", "2027-08-31"),
    }

    for season, values in dates.items():

        first = min(values).date().isoformat()
        last = max(values).date().isoformat()

        lower, upper = expected_ranges[season]

        assert lower <= first <= upper
        assert lower <= last <= upper


def test_team_compare_handles_non_pl_seasons():

    result = query_lab.team_compare(
        "Bournemouth",
        [
            "2016-17",
            "2017-18",
            "2018-19",
            "2019-20",
            "2020-21",
            "2021-22",
            "2022-23",
            "2023-24",
            "2024-25",
            "2025-26",
        ],
    )

    returned = {
        row["season"]
        for row in result["seasons"]
    }

    skipped = {
        row["season"]
        for row in result["skipped_seasons"]
    }

    assert "2016-17" in returned
    assert "2018-19" in returned
    assert "2019-20" in returned
    assert "2020-21" in skipped
    assert "2021-22" in skipped
    assert "2022-23" in returned
    assert "2023-24" in returned
    assert "2024-25" in returned
    assert "2025-26" in returned

    assert all(
        row["complete"]
        for row in result["seasons"]
    )



def test_head_to_head():

    # --------------------------------------------------------
    # Case 1: Club with PL gaps versus continuously present club
    # --------------------------------------------------------

    city_bournemouth = query_lab.head_to_head(
        "Man City",
        "Bournemouth",
        [
            "2019-20",
            "2020-21",
            "2021-22",
            "2022-23",
        ],
    )

    assert (
        city_bournemouth["summary"]["matches"]
        == 4
    )

    assert (
        city_bournemouth["summary"]["wins"]
        == 4
    )

    assert (
        city_bournemouth["summary"]["draws"]
        == 0
    )

    assert (
        city_bournemouth["summary"]["losses"]
        == 0
    )

    skipped = {
        row["season"]
        for row
        in city_bournemouth["skipped_seasons"]
    }

    assert skipped == {
        "2020-21",
        "2021-22",
    }

    # Every returned fixture must have a valid result.
    assert all(
        row["team_result"]
        in {"W", "D", "L", "UNPLAYED"}
        for row
        in city_bournemouth["matches"]
    )

    # --------------------------------------------------------
    # Case 2: H2H must be symmetric
    # --------------------------------------------------------

    bournemouth_city = query_lab.head_to_head(
        "Bournemouth",
        "Man City",
        [
            "2019-20",
            "2020-21",
            "2021-22",
            "2022-23",
        ],
    )

    assert (
        bournemouth_city["summary"]["matches"]
        == city_bournemouth["summary"]["matches"]
    )

    assert (
        bournemouth_city["summary"]["wins"]
        == city_bournemouth["summary"]["losses"]
    )

    assert (
        bournemouth_city["summary"]["draws"]
        == city_bournemouth["summary"]["draws"]
    )

    assert (
        bournemouth_city["summary"]["losses"]
        == city_bournemouth["summary"]["wins"]
    )

    assert (
        bournemouth_city["summary"]["goals_for"]
        == city_bournemouth["summary"]["goals_against"]
    )

    assert (
        bournemouth_city["summary"]["goals_against"]
        == city_bournemouth["summary"]["goals_for"]
    )

    # --------------------------------------------------------
    # Case 3: Two clubs present in every dataset season
    # --------------------------------------------------------

    arsenal_city = query_lab.head_to_head(
        "Arsenal",
        "Man City",
        [
            "2016-17",
            "2017-18",
            "2018-19",
            "2019-20",
            "2020-21",
            "2021-22",
            "2022-23",
            "2023-24",
            "2024-25",
            "2025-26",
        ],
    )

    # Two league meetings per shared season.
    assert (
        arsenal_city["summary"]["matches"]
        == 20
    )

    assert (
        arsenal_city["skipped_seasons"]
        == []
    )

    # --------------------------------------------------------
    # Case 4: Aggregate W/D/L must reconcile with fixtures
    # --------------------------------------------------------

    matches = arsenal_city["matches"]

    assert (
        sum(
            row["team_result"] == "W"
            for row in matches
        )
        == arsenal_city["summary"]["wins"]
    )

    assert (
        sum(
            row["team_result"] == "D"
            for row in matches
        )
        == arsenal_city["summary"]["draws"]
    )

    assert (
        sum(
            row["team_result"] == "L"
            for row in matches
        )
        == arsenal_city["summary"]["losses"]
    )

    assert (
        arsenal_city["summary"]["wins"]
        + arsenal_city["summary"]["draws"]
        + arsenal_city["summary"]["losses"]
        == arsenal_city["summary"]["matches"]
    )

    # --------------------------------------------------------
    # Case 5: Every played fixture's result must agree with
    # the score and the selected team
    # --------------------------------------------------------

    for row in matches:

        home_score = int(
            row["home_score"]
        )

        away_score = int(
            row["away_score"]
        )

        if (
            row["home_team_name"]
            == arsenal_city["team"]
        ):
            team_score = home_score
            opponent_score = away_score
        else:
            team_score = away_score
            opponent_score = home_score

        if team_score > opponent_score:
            expected = "W"
        elif team_score < opponent_score:
            expected = "L"
        else:
            expected = "D"

        assert (
            row["team_result"]
            == expected
        )


def test_team_form():
    result = query_lab.team_form(
        season="2024-25",
        team="Liverpool",
    )

    completed = result["matches"]

    assert completed

    assert all(
        row["result"] in {"W", "D", "L"}
        for row in completed
    )

    assert all(
        row["points"] in {0, 1, 3}
        for row in completed
    )

    assert all(
        row["goals_for"] >= 0
        and row["goals_against"] >= 0
        for row in completed
    )

    assert all(
        row["goal_difference"]
        == row["goals_for"]
        - row["goals_against"]
        for row in completed
    )

    assert all(
        completed[i]["kickoff_time"]
        <= completed[i + 1]["kickoff_time"]
        for i in range(len(completed) - 1)
    )

    assert result["windows"]["3"]["matches"] <= 3
    assert result["windows"]["5"]["matches"] <= 5

    assert (
        result["streaks"]["current_win_streak"]
        <= len(completed)
    )

    assert (
        result["streaks"]["current_unbeaten_streak"]
        <= len(completed)
    )

    assert (
        result["streaks"]["current_loss_streak"]
        <= len(completed)
    )

    assert (
        result["streaks"]["current_clean_sheet_streak"]
        <= len(completed)
    )

    assert (
        result["streaks"]["current_scoring_streak"]
        <= len(completed)
    )

    assert result["excluded_unplayed"] == 0

    assert all(
        row["home_score"] != ""
        and row["away_score"] != ""
        for row in completed
    )


if __name__ == "__main__":
    tests = [
        test_seasons,
        test_top_goals,
        test_player_total,
        test_query_provenance,
        test_identity_registry,
        test_man_city_identity,
        test_bournemouth_identity,
        test_named_fixture_query,
        test_named_opponent_query,
        test_verified_fixture_correction,
    test_fixture_season_partitions,
test_team_compare_handles_non_pl_seasons,
        test_head_to_head,
        test_team_form,
    ]

    failures = []

    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except Exception as exc:
            failures.append((test.__name__, str(exc)))
            print(f"FAIL  {test.__name__}: {exc}")

    print()

    if failures:
        print(f"FAILED: {len(failures)} test(s)")
        raise SystemExit(1)

    print(f"PASSED: {len(tests)} test(s)")
    raise SystemExit(0)


