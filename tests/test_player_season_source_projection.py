from __future__ import annotations

import csv
import json

import player_season_source_projection
import rich_player_projection
from scripts import materialize_player_season_source_stats


def _write_csv(path, fieldnames, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_direct_player_code_attaches_source_native_forward_passes(
    monkeypatch,
    tmp_path,
) -> None:
    packaged = tmp_path / "player_season.csv"
    _write_csv(
        packaged,
        ["season", "source_player_id", "forward_passes"],
        [{
            "season": "2026-27",
            "source_player_id": "184029",
            "forward_passes": "45.0",
        }],
    )
    monkeypatch.setattr(player_season_source_projection, "PACKAGED", packaged)
    player_season_source_projection.clear_caches()
    try:
        enriched = player_season_source_projection.enrich_player(
            {"player_code": "184029"},
            "2026-27",
        )
        assert enriched["forward_passes"] == 45.0
        assert enriched["_player_season_source_player_id"] == "184029"
        assert enriched["_player_season_identity_route"] == (
            "FPL_PLAYER_CODE_TO_PLAYER_SEASON_PLAYER_ID_EXACT"
        )
    finally:
        player_season_source_projection.clear_caches()


def test_historical_attachment_uses_only_verified_identity_edges(
    monkeypatch,
    tmp_path,
) -> None:
    packaged = tmp_path / "player_season.csv"
    registry = tmp_path / "identity.csv"
    rich = tmp_path / "rich.csv"
    _write_csv(
        packaged,
        ["season", "source_player_id", "forward_passes"],
        [{
            "season": "2024-25",
            "source_player_id": "184029",
            "forward_passes": "445.0",
        }],
    )
    _write_csv(
        registry,
        ["season", "fpl_element", "source_player_id", "identity_status"],
        [{
            "season": "2024-25",
            "fpl_element": "13",
            "source_player_id": "547410",
            "identity_status": "VERIFIED",
        }],
    )
    _write_csv(
        rich,
        ["season", "player_code", "source_player_id"],
        [{
            "season": "2024-25",
            "player_code": "184029",
            "source_player_id": "547410",
        }],
    )
    monkeypatch.setattr(player_season_source_projection, "PACKAGED", packaged)
    monkeypatch.setattr(
        player_season_source_projection,
        "IDENTITY_REGISTRY",
        registry,
    )
    monkeypatch.setattr(rich_player_projection, "PACKAGED", rich)
    player_season_source_projection.clear_caches()
    rich_player_projection.clear_caches()
    try:
        enriched = player_season_source_projection.enrich_player(
            {"player_code": "13"},
            "2024-25",
        )
        assert enriched["forward_passes"] == 445.0
        assert enriched["_player_season_source_player_id"] == "184029"
        assert enriched["_player_season_identity_route"] == (
            "FPL_ELEMENT_TO_VERIFIED_PLAYER_MATCH_ID_"
            "TO_PLAYER_SEASON_PLAYER_ID"
        )
    finally:
        player_season_source_projection.clear_caches()
        rich_player_projection.clear_caches()


def test_unresolved_identity_and_source_blank_remain_unavailable(
    monkeypatch,
    tmp_path,
) -> None:
    packaged = tmp_path / "player_season.csv"
    _write_csv(
        packaged,
        ["season", "source_player_id", "forward_passes"],
        [{
            "season": "2026-27",
            "source_player_id": "184029",
            "forward_passes": "",
        }],
    )
    monkeypatch.setattr(player_season_source_projection, "PACKAGED", packaged)
    player_season_source_projection.clear_caches()
    try:
        observed = player_season_source_projection.enrich_player(
            {"player_code": "184029"},
            "2026-27",
        )
        unresolved = player_season_source_projection.enrich_player(
            {"player_code": "999999"},
            "2026-27",
        )
        assert observed["forward_passes"] is None
        assert unresolved["forward_passes"] is None
        assert unresolved["_player_season_source_projection"] == "UNAVAILABLE"
    finally:
        player_season_source_projection.clear_caches()


def test_materializer_deduplicates_equal_rows_and_records_provenance(
    tmp_path,
) -> None:
    source = tmp_path / "pl_stats"
    fields = ["playerId", "forwardPasses"]
    row = {"playerId": "184029", "forwardPasses": "45"}
    _write_csv(
        source / "Arsenal_3" / "players_stats" / "2026-27_players_stats.csv",
        fields,
        [row],
    )
    _write_csv(
        source / "Duplicate_99" / "players_stats" / "2026-27_players_stats.csv",
        fields,
        [row],
    )
    output = tmp_path / "projection.csv"
    metadata = tmp_path / "projection.metadata.json"

    counts = materialize_player_season_source_stats.materialize(
        source,
        ("2026-27",),
        output,
        metadata,
        "test-sha",
        "2026-09-09T00:00:00Z",
    )

    assert counts == {"2026-27": 1}
    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows == [{
        "season": "2026-27",
        "source_player_id": "184029",
        "forward_passes": "45.0",
    }]
    payload = json.loads(metadata.read_text(encoding="utf-8"))
    assert payload["source_release_sha"] == "test-sha"
    assert payload["missingness_policy"] == "SOURCE_BLANK_IS_UNAVAILABLE_NOT_ZERO"
