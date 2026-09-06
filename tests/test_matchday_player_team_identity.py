from __future__ import annotations

import matchday_pack


def _player_row(*, team_code: str, identity_key: str, first_name: str, second_name: str) -> dict:
    return {
        "frl_season": "2026-27",
        "frl_team_id": team_code,
        "frl_fixture_relationship_status": "VERIFIED",
        "frl_fixture_id": "20",
        "frl_player_identity_key": identity_key,
        "source_player_code": identity_key,
        "source_first_name": first_name,
        "source_second_name": second_name,
        "source_position": "MID",
        "source_minutes": "90",
        "source_goals_scored": "1",
        "source_expected_goals": "0.5",
        "source_assists": "0",
        "source_expected_assists": "0.2",
        "source_yellow_cards": "0",
        "source_red_cards": "0",
        "source_tackles": "2",
        "source_recoveries": "4",
        "source_defensive_contribution": "6",
    }


def test_player_recent_side_uses_persistent_team_code_not_season_local_id(monkeypatch):
    fixture = {
        "season": "2026-27",
        "home_team_id": "1",
        "kickoff_time": "2026-09-06T15:30:00Z",
    }

    monkeypatch.setattr(
        matchday_pack,
        "_identity",
        lambda season, local_id: {
            "display_name": "Arsenal",
            "persistent_team_code": "3",
        },
    )
    monkeypatch.setattr(
        matchday_pack,
        "_fpl_rows",
        lambda: (
            _player_row(
                team_code="3",
                identity_key="arsenal-player",
                first_name="A",
                second_name="Arsenal",
            ),
            _player_row(
                team_code="1",
                identity_key="united-player",
                first_name="M",
                second_name="United",
            ),
        ),
    )
    monkeypatch.setattr(
        matchday_pack.query_lab,
        "load_fixtures",
        lambda: [
            {
                "season": "2026-27",
                "fixture_id": "20",
                "kickoff_time": "2026-08-30T15:00:00Z",
            }
        ],
    )

    side = matchday_pack._player_recent_side(fixture, "home")
    goal_names = [player["player_name"] for player in side["leaderboards"][0]["players"]]

    assert goal_names == ["A Arsenal"]
    assert "M United" not in goal_names
