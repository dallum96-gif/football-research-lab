from __future__ import annotations

from datetime import datetime

import matchday_pack


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


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


def test_current_matchday_fixture_menu_is_source_backed() -> None:
    fixtures = matchday_pack.fixture_options("2026-27")

    assert len(fixtures) == 380
    assert all(fixture["season"] == "2026-27" for fixture in fixtures)
    assert len({fixture["fixture_id"] for fixture in fixtures}) == 380
    assert {fixture["gameweek"] for fixture in fixtures if fixture["gameweek"] is not None}


def test_matchday_pack_recent_team_windows_are_strictly_pre_kickoff() -> None:
    fixtures = matchday_pack.fixture_options("2026-27")
    target = next(fixture for fixture in fixtures if not fixture["completed"])
    pack = matchday_pack.build_matchday_pack("2026-27", target["fixture_id"])
    target_time = _dt(str(pack["fixture"]["kickoff_time"]))

    for side in ("home", "away"):
        team = pack["teams"][side]
        assert team["sample_size"] <= 5
        assert len(team["matches"]) == team["sample_size"]
        assert team["current_season_sample_size"] <= team["sample_size"]
        assert all(_dt(str(match["kickoff_time"])) < target_time for match in team["matches"])


def test_matchday_player_metric_missingness_does_not_become_zero() -> None:
    total, observed = matchday_pack._observed_player_metric(
        [{"source_tackles": ""}],
        "source_tackles",
    )
    assert total is None
    assert observed == 0

    total, observed = matchday_pack._observed_player_metric(
        [{"source_tackles": "0"}],
        "source_tackles",
    )
    assert total == 0.0
    assert observed == 1


def test_matchday_player_side_uses_persistent_team_code_not_season_local_id(monkeypatch) -> None:
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


def test_matchday_pack_reports_current_evidence_maturity() -> None:
    fixtures = matchday_pack.fixture_options("2026-27")
    target = next(fixture for fixture in fixtures if not fixture["completed"])
    pack = matchday_pack.build_matchday_pack("2026-27", target["fixture_id"])

    maturity = pack["data_maturity"]
    assert maturity["status"] in {"EARLY_SEASON", "RECENT_WINDOW_MATURE"}
    assert set(maturity["team_current_season_matches"]) == {"home", "away"}
    assert set(maturity["player_fixture_evidence_matches"]) == {"home", "away"}


def test_matchday_pack_exposes_player_tiles_and_poisson_without_fake_foul_model() -> None:
    fixtures = matchday_pack.fixture_options("2026-27")
    target = next(fixture for fixture in fixtures if not fixture["completed"])
    pack = matchday_pack.build_matchday_pack("2026-27", target["fixture_id"])

    assert pack["prediction"]["status"] == "AVAILABLE"
    assert pack["prediction"]["model"] == "Poisson V1.0"

    for side in ("home", "away"):
        leaderboards = pack["players"][side]["leaderboards"]
        assert {board["key"] for board in leaderboards} >= {"xg", "xa", "cards", "tackles"}
        assert all(len(board["players"]) <= 5 for board in leaderboards)

    card_matchup = pack["matchups"]["cards"]
    assert card_matchup["status"] == "PARTIAL"
    assert any("fouls" in item for item in card_matchup["withheld"])
