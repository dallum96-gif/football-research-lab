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
    *player_profile_source_projection.PROFILE_SOURCE_FIELDS,
]


def _write_csv(path, fieldnames, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _profile_row(**overrides):
    row = {field: "" for field in PROFILE_FIELDS}
    row.update({
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
    })
    row.update(overrides)
    return row


def test_profile_per90_and_participation_use_same_source_representation(monkeypatch, tmp_path) -> None:
    packaged = tmp_path / "profile.csv"
    _write_csv(packaged, PROFILE_FIELDS, [_profile_row()])
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
    _write_csv(packaged, PROFILE_FIELDS, [_profile_row(source_starts="")])
    monkeypatch.setattr(player_profile_source_projection, "PACKAGED", packaged)
    player_profile_source_projection.clear_caches()
    try:
        row = player_profile_source_projection.season_rows("2026-27")["184029"]
        assert player_profile_source_projection.complete_participation(row) is None
    finally:
        player_profile_source_projection.clear_caches()


def test_position_templates_are_six_axis_and_distinct() -> None:
    assert set(player_profile_source_projection.POSITION_PROFILE_METRICS) == {
        "GKP", "DEF", "MID", "FWD"
    }
    for position, definitions in player_profile_source_projection.POSITION_PROFILE_METRICS.items():
        assert len(definitions) == 6, position
        keys = [definition["key"] for definition in definitions]
        labels = [definition["label"] for definition in definitions]
        assert len(set(keys)) == 6
        assert len(set(labels)) == 6


def test_same_row_ratio_and_derived_metrics() -> None:
    row = {
        "source_minutes": 180.0,
        "aerial_duels_won": 6.0,
        "aerial_duels": 10.0,
        "total_tackles": 8.0,
        "total_shots": 8.0,
        "shots_on_target": 4.0,
        "expected_goals_on_target_conceded": 5.5,
        "goals_conceded": 4.0,
        "saves_made": 12.0,
        "gk_successful_distribution": 40.0,
        "gk_unsuccessful_distribution": 10.0,
        "catches": 4.0,
        "punches": 2.0,
    }
    defender_aerial = player_profile_source_projection.POSITION_PROFILE_METRICS["DEF"][0]
    defender_tackling = player_profile_source_projection.POSITION_PROFILE_METRICS["DEF"][1]
    forward_accuracy = player_profile_source_projection.POSITION_PROFILE_METRICS["FWD"][5]
    keeper_stopping = player_profile_source_projection.POSITION_PROFILE_METRICS["GKP"][0]
    keeper_save_rate = player_profile_source_projection.POSITION_PROFILE_METRICS["GKP"][1]
    keeper_claiming = player_profile_source_projection.POSITION_PROFILE_METRICS["GKP"][3]
    keeper_distribution = player_profile_source_projection.POSITION_PROFILE_METRICS["GKP"][5]

    assert player_profile_source_projection.metric_value(row, defender_aerial) == 60.0
    assert player_profile_source_projection.metric_value(row, defender_tackling) == 4.0
    assert player_profile_source_projection.metric_value(row, forward_accuracy) == 50.0
    assert abs(
        player_profile_source_projection.metric_value(row, keeper_stopping)
        - ((5.5 - 4.0) / 180 * 90)
    ) < 1e-12
    assert player_profile_source_projection.metric_value(row, keeper_save_rate) == 75.0
    assert player_profile_source_projection.metric_value(row, keeper_claiming) == 3.0
    assert player_profile_source_projection.metric_value(row, keeper_distribution) == 80.0


def test_profile_materializer_preserves_fields_for_all_position_templates(tmp_path) -> None:
    root = tmp_path / "pl_stats"
    source = root / "_merged" / "players" / "2026-27_players_stats.csv"
    source_fields = [
        "playerId",
        "playerName",
        "position",
        *dict.fromkeys(materialize_player_profile_source_stats.SOURCE_FIELDS.values()),
    ]
    source_row = {field: "" for field in source_fields}
    source_row.update({
        "playerId": "154561",
        "playerName": "David Raya",
        "position": "Goalkeeper",
        "gamesPlayed": "3",
        "starts": "3",
        "timePlayed": "270",
        "totalShots": "8",
        "shotsOnTargetIncGoals": "4",
        "expectedGoalsOnTargetConceded": "4.5",
        "goalsConceded": "3",
        "savesMade": "9",
        "catches": "4",
        "punches": "1",
        "goalkeeperSmother": "2",
        "gkSuccessfulDistribution": "60",
        "gkUnsuccessfulDistribution": "15",
    })
    _write_csv(source, source_fields, [source_row])

    rows = materialize_player_profile_source_stats.materialize_season(root, "2026-27")
    assert len(rows) == 1
    row = rows[0]
    assert row["source_player_id"] == "154561"
    assert row["source_minutes"] == "270.0"
    assert row["total_shots"] == "8.0"
    assert row["shots_on_target"] == "4.0"
    assert row["expected_goals_on_target_conceded"] == "4.5"
    assert row["goals_conceded"] == "3.0"
    assert row["saves_made"] == "9.0"
    assert row["gk_successful_distribution"] == "60.0"
