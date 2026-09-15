from __future__ import annotations

import player_profile_identity


def test_current_and_historical_odegaard_share_one_research_identity() -> None:
    current = player_profile_identity.resolve_route_identity("2026-27", "184029")
    historical = player_profile_identity.resolve_route_identity("2024-25", "13")

    assert current["available"] is True
    assert historical["available"] is True
    assert current["player_identity_key"] == "player_match:547410"
    assert historical["player_identity_key"] == current["player_identity_key"]
    assert current["portrait_player_code"] == "184029"
    assert historical["portrait_player_code"] == "184029"


def test_odegaard_cross_season_navigation_uses_each_seasons_route_code() -> None:
    options = player_profile_identity.profile_seasons("2026-27", "184029")
    by_season = {row["season"]: row for row in options}

    assert by_season["2026-27"]["player_code"] == "184029"
    assert by_season["2024-25"]["player_code"] == "13"


def test_unresolved_identity_fails_closed() -> None:
    result = player_profile_identity.resolve_player_identity(
        "2026-27",
        {
            "player_code": "999999999",
            "_records": [{"element": "999999999"}],
        },
    )

    assert result["available"] is False
    assert result["identity_status"] == "UNRESOLVED"
    assert result["player_identity_key"] is None
    assert result["portrait_player_code"] is None
