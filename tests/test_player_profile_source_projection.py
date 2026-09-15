from __future__ import annotations

import csv

import player_profile_source_projection
from scripts import materialize_player_profile_source_stats


PROFILE_FIELDS = [
    "season",
    "source_player_id",
    "source_player_name",
    "source_position",
    "source_appearances",
    "source_starts",
    "source_minutes",
    "expected_goals",
    "expected_assists",
    "accurate_opposition_half_passes",
    "forward_passes",
    "recoveries",
    "tackles_won",
]


def _write_csv(path, fieldnames, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_profile_per90_and_participation_use_same_source_representation(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "profile.csv"
    _write_csv(
        packaged,
        PROFILE_FIELDS,
        [{
            "season": "2026-27",
            "source_player_id": "184029",
            "source_player_name": "Martin Ødegaard",
            "source_position": "Midfielder",
            "source_appearances": "3",
            "source_starts": "3",
            "source_minutes": "224",
            "expected_goals": "1.001",
            "expected_assists": "1.0473",
            "accurate_opposition_half_passes": "106",
            "forward_passes": "45",
            "recoveries": "8",
            "tackles_won": "3",
        }],
    )
    monkeypatch.setattr(player_profile_source_projection, "PACKAGED", packaged)
    player_profile_source_projection.clear_caches()
    try:
        row = player_profile_source_projection.season_rows("2026-27")["184029"]
        assert player_profile_source_projection.complete_participation(row) == {
            "appearances": 3,
            "starts": 3,
            "minutes": 224,
        }
        assert abs(
            player_profile_source_projection.per_90(row, "forward_passes")
            - (45 / 224 * 90)
        ) < 1e-12
    finally:
        player_profile_source_projection.clear_caches()


def test_incomplete_source_participation_fails_closed_as_one_block(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "profile.csv"
    _write_csv(
        packaged,
        PROFILE_FIELDS,
        [{
            "season": "2026-27",
            "source_player_id": "184029",
            "source_player_name": "Martin Ødegaard",
            "source_position": "Midfielder",
            "source_appearances": "3",
            "source_starts": "",
            "source_minutes": "224",
            "expected_goals": "1.001",
            "expected_assists": "1.0473",
            "accurate_opposition_half_passes": "106",
            "forward_passes": "45",
            "recoveries": "8",
            "tackles_won": "3",
        }],
    )
    monkeypatch.setattr(player_profile_source_projection, "PACKAGED", packaged)
    player_profile_source_projection.clear_caches()
    try:
        row = player_profile_source_projection.season_rows("2026-27")["184029"]
        assert player_profile_source_projection.complete_participation(row) is None
    finally:
        player_profile_source_projection.clear_caches()


def test_profile_materializer_preserves_participation_and_six_axes(tmp_path) -> None:
    root = tmp_path / "pl_stats"
    source = root / "_merged" / "players" / "2026-27_players_stats.csv"
    _write_csv(
        source,
        [
            "playerId",
            "playerName",
            "position",
            "gamesPlayed",
            "starts",
            "timePlayed",
            "expectedGoals",
            "expectedAssists",
            "successfulPassesOppositionHalf",
            "forwardPasses",
            "recoveries",
            "tacklesWon",
        ],
        [{
            "playerId": "184029",
            "playerName": "Martin Ødegaard",
            "position": "Midfielder",
            "gamesPlayed": "3",
            "starts": "3",
            "timePlayed": "224",
            "expectedGoals": "1.001",
            "expectedAssists": "1.0473",
            "successfulPassesOppositionHalf": "106",
            "forwardPasses": "45",
            "recoveries": "8",
            "tacklesWon": "3",
        }],
    )

    rows = materialize_player_profile_source_stats.materialize_season(root, "2026-27")
    assert rows == [{
        "season": "2026-27",
        "source_player_id": "184029",
        "source_player_name": "Martin Ødegaard",
        "source_position": "Midfielder",
        "source_appearances": "3.0",
        "source_starts": "3.0",
        "source_minutes": "224.0",
        "expected_goals": "1.001",
        "expected_assists": "1.0473",
        "accurate_opposition_half_passes": "106.0",
        "forward_passes": "45.0",
        "recoveries": "8.0",
        "tackles_won": "3.0",
    }]
