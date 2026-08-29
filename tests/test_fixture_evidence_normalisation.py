from __future__ import annotations

from pulselive_fixture_evidence import normalise_events, normalise_lineups


def test_event_normalisation_preserves_goal_assist_card_and_substitution() -> None:
    payload = {
        "homeTeam": {
            "teamId": "10",
            "goals": [{"id": "g1", "playerId": "101", "assistPlayerId": "102", "time": "31", "goalType": "REGULAR"}],
            "cards": [{"id": "c1", "playerId": "103", "time": "44", "type": "YELLOW"}],
            "subs": [{"id": "s1", "playerOnId": "104", "playerOffId": "105", "time": "70"}],
        },
        "awayTeam": {"teamId": "20", "goals": [], "cards": [], "subs": []},
    }
    events = normalise_events(payload)
    assert [row["type"] for row in events] == ["goal", "card", "substitution"]
    assert events[0]["primary_source_player_id"] == "101"
    assert events[0]["secondary_source_player_id"] == "102"
    assert events[1]["detail"]["card_type"] == "YELLOW"
    assert events[2]["primary_source_player_id"] == "104"
    assert events[2]["secondary_source_player_id"] == "105"


def test_lineup_normalisation_preserves_formation_managers_and_players() -> None:
    payload = {
        "home_team": {
            "teamId": "10",
            "formation": {
                "formation": "4-2-3-1",
                "lineup": {"players": [{"playerId": "101", "x": 50, "y": 10}]},
            },
            "players": [{"playerId": "101", "displayName": "Example", "position": "GK", "shirtNum": "1"}],
            "managers": [{"id": "m1", "firstName": "Alex", "lastName": "Example", "type": "manager"}],
        },
        "away_team": {
            "teamId": "20",
            "formation": {"formation": "4-3-3", "lineup": {}},
            "players": [{"playerId": "201", "displayName": "Away Example", "position": "ST", "shirtNum": "9"}],
            "managers": [{"id": "m2", "firstName": "Jamie", "lastName": "Example", "type": "manager"}],
        },
    }
    result = normalise_lineups(payload)
    assert result["team_context"] == {"home": "10", "away": "20"}
    assert result["formations"]["home"] == {"status": "AVAILABLE", "value": "4-2-3-1"}
    assert result["formations"]["away"] == {"status": "AVAILABLE", "value": "4-3-3"}
    assert result["managers"]["status"] == "AVAILABLE"
    assert result["players"][0]["source_player_id"] == "101"


def test_lineup_placement_requires_explicit_coordinates() -> None:
    payload = {
        "homeTeam": {
            "teamId": "10",
            "formation": {
                "formation": "4-2-3-1",
                "lineup": {"players": [{"playerId": "101", "position": "GK"}]},
            },
            "players": [{"playerId": "101", "displayName": "Example", "position": "GK"}],
        },
        "awayTeam": {"teamId": "20", "formation": {"formation": "4-3-3"}, "players": []},
    }
    result = normalise_lineups(payload)
    assert result["placements"]["home"] == []


def test_lineup_normalisation_preserves_source_formation_line_order() -> None:
    payload = {
        "home_team": {
            "teamId": "10",
            "formation": {
                "formation": "4-2-3-1",
                "lineup": [
                    ["101"],
                    ["102", "103", "104", "105"],
                    ["106", "107"],
                    ["108", "109", "110"],
                    ["111"],
                ],
            },
            "players": [
                {"id": str(player_id), "firstName": f"Player {player_id}", "position": "Goalkeeper" if player_id == 101 else "Outfield"}
                for player_id in range(101, 112)
            ],
        },
        "away_team": {"teamId": "20", "players": []},
    }

    result = normalise_lineups(payload)
    by_player = {row["source_player_id"]: row for row in result["players"]}

    assert result["formations"]["home"] == {"status": "AVAILABLE", "value": "4-2-3-1"}
    assert by_player["101"]["source_formation_order"] == {
        "line_index": 0,
        "slot_index": 0,
        "line_size": 1,
    }
    assert by_player["104"]["source_formation_order"] == {
        "line_index": 1,
        "slot_index": 2,
        "line_size": 4,
    }
    assert by_player["111"]["source_formation_order"] == {
        "line_index": 4,
        "slot_index": 0,
        "line_size": 1,
    }
    assert result["placements"]["home"] == []
