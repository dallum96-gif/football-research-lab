from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "materialize_incremental_fpl_season.py"
spec = importlib.util.spec_from_file_location("materialize_incremental_fpl_season", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "upstream"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "FRL Test")

    pm = repo / "pl_stats" / "Arsenal" / "players_match_stats"
    pm.mkdir(parents=True)
    (pm / "2025-26_players_match_stats.csv").write_text(
        "pl_code,playerId\n1001,9001\n1002,9002\n",
        encoding="utf-8",
    )

    fpl = repo / "fpl_scraper" / "fpl_stats"
    (fpl / "fixtures").mkdir(parents=True)
    (fpl / "_merged" / "players").mkdir(parents=True)
    (fpl / "_index").mkdir(parents=True)
    (fpl / "fixtures" / "2026-27_all_fixtures.csv").write_text("id,code\n1,5001\n", encoding="utf-8")
    (fpl / "_merged" / "players" / "2026-27_all_players_gw.csv").write_text(
        "element,player_code\n1,1001\n", encoding="utf-8"
    )
    (fpl / "_index" / "_players_index.json").write_text("{}\n", encoding="utf-8")
    (fpl / "_index" / "_teams_index.json").write_text("{}\n", encoding="utf-8")
    (fpl / "fixtures" / "2025-26_all_fixtures.csv").write_text("id,code\n1,4001\n", encoding="utf-8")
    (fpl / "_merged" / "players" / "2025-26_all_players_gw.csv").write_text(
        "element,player_code\n1,1001\n", encoding="utf-8"
    )

    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")
    return repo, _git(repo, "rev-parse", "HEAD")


def test_player_match_bridge_reads_pinned_git_objects_not_dirty_worktree(tmp_path: Path) -> None:
    repo, commit = _init_repo(tmp_path)
    root = repo / "pl_stats"

    before, seasons_before, meta_before = module._player_match_bridge(root, source_commit=commit)

    tracked = root / "Arsenal" / "players_match_stats" / "2025-26_players_match_stats.csv"
    tracked.write_text("pl_code,playerId\n1001,9999\n", encoding="utf-8")
    extra = root / "Chelsea" / "players_match_stats"
    extra.mkdir(parents=True)
    (extra / "2024-25_players_match_stats.csv").write_text(
        "pl_code,playerId\n7777,7777\n", encoding="utf-8"
    )

    after, seasons_after, meta_after = module._player_match_bridge(root, source_commit=commit)

    assert before == after == {"1001": {"9001"}, "1002": {"9002"}}
    assert seasons_before == seasons_after == {"1001": {"2025-26"}, "1002": {"2025-26"}}
    assert meta_before["evidence_set_sha256"] == meta_after["evidence_set_sha256"]
    assert meta_after["read_mode"] == "PINNED_GIT_OBJECTS"
    assert meta_after["canonical_file_count"] == 1


def test_consumed_fpl_source_file_reads_pinned_git_object_not_worktree(tmp_path: Path) -> None:
    repo, commit = _init_repo(tmp_path)
    source_root = repo / "fpl_scraper" / "fpl_stats"
    paths = module._season_source_paths(source_root, "2026-27")

    metadata_before = module._source_metadata(
        paths, source_root, repo_root=repo, source_commit=commit
    )
    rows_before, fields_before, payload_before = module._pinned_csv(
        paths["fixtures"], repo_root=repo, source_commit=commit
    )

    # Simulate a Windows checkout/dirty tree: CRLF plus changed data.  The
    # materialiser must still consume the exact immutable Git object bytes.
    paths["fixtures"].write_bytes(b"id,code\r\n1,9999\r\n")

    metadata_after = module._source_metadata(
        paths, source_root, repo_root=repo, source_commit=commit
    )
    rows_after, fields_after, payload_after = module._pinned_csv(
        paths["fixtures"], repo_root=repo, source_commit=commit
    )

    assert metadata_before == metadata_after
    assert metadata_after["fixtures"]["git_object_sha256"] == metadata_after["fixtures"]["sha256"]
    assert metadata_after["fixtures"]["read_mode"] == "PINNED_GIT_OBJECT"
    assert payload_before == payload_after
    assert fields_before == fields_after == ("id", "code")
    assert rows_before == rows_after == [{"id": "1", "code": "5001"}]


def test_fixture_completion_keeps_real_zero_scores_and_missing_scheduled_scores_distinct() -> None:
    teams = {
        "1": {"persistent_team_code": "A"},
        "2": {"persistent_team_code": "B"},
    }
    source_rows = [
        {
            "id": "1", "code": "101", "team_h": "1", "team_a": "2",
            "finished": "true", "started": "true", "team_h_score": "0", "team_a_score": "0",
            "kickoff_time": "2026-08-15T12:00:00Z", "event": "1",
        },
        {
            "id": "2", "code": "102", "team_h": "2", "team_a": "1",
            "finished": "true", "started": "true", "team_h_score": "0", "team_a_score": "1",
            "kickoff_time": "2026-08-16T12:00:00Z", "event": "1",
        },
        {
            "id": "3", "code": "103", "team_h": "1", "team_a": "2",
            "finished": "false", "started": "false", "team_h_score": "", "team_a_score": "",
            "kickoff_time": "2026-09-01T12:00:00Z", "event": "3",
        },
    ]

    rows = module.build_canonical_fixtures(source_rows, season="2026-27", teams_by_local_id=teams)
    assert (rows[0]["home_score"], rows[0]["away_score"]) == ("0", "0")
    assert (rows[1]["home_score"], rows[1]["away_score"]) == ("0", "1")
    assert (rows[2]["home_score"], rows[2]["away_score"]) == ("", "")


def test_identity_classes_and_capability_state_do_not_overclaim_canonical_resolution() -> None:
    player_rows = [
        {"element": "1", "player_code": "1001", "team_code": "10", "minutes": "90", "starts": "1", "expected_goals": "0.5"},
        {"element": "2", "player_code": "1002", "team_code": "10", "minutes": "0", "starts": "0", "expected_goals": "0.0"},
        {"element": "3", "player_code": "1003", "team_code": "20", "minutes": "0", "starts": "0", "expected_goals": "0.0"},
        {"element": "4", "player_code": "1004", "team_code": "20", "minutes": "0", "starts": "0", "expected_goals": "0.0"},
    ]
    identities = module.build_player_identities(
        player_rows,
        season="2026-27",
        bridge_candidates={
            "1001": {"9001"},
            "1002": {"9002"},
            "1004": {"9004", "9904"},
        },
        bridge_seasons={
            "1001": {"2025-26"},
            "1002": {"2025-26"},
            "1004": {"2024-25", "2025-26"},
        },
        registered_source_player_ids={"9001"},
        source_commit="abc123",
        source_path="_merged/players/2026-27_all_players_gw.csv",
        source_sha256="deadbeef",
    )

    by_element = {row["fpl_element"]: row for row in identities}
    assert by_element["1"]["identity_status"] == "VERIFIED"
    assert by_element["2"]["identity_status"] == "SOURCE_NATIVE_VERIFIED"
    assert "PLAYER_MATCH" in by_element["2"]["identity_route"]
    assert by_element["3"]["identity_status"] == "SOURCE_NATIVE_VERIFIED"
    assert by_element["3"]["identity_route"] == "SOURCE_NATIVE_FPL_PLAYER_CODE"
    assert by_element["4"]["identity_status"] == "AMBIGUOUS"

    canonical_rows = [
        {
            "season": "2026-27", "fixture_id": "1", "fixture_code": "101", "kickoff_time": "",
            "gameweek": "1", "home_team_id": "1", "away_team_id": "2", "home_score": "0", "away_score": "0",
        }
    ]
    register = module._capability_register(
        season="2026-27",
        source_commit="abc123",
        retrieved_at="2026-08-31T12:00:00Z",
        canonical_rows=canonical_rows,
        player_rows=player_rows,
        identity_rows=identities,
    )
    player_identity = next(item for item in register["capabilities"] if item["capability"] == "player_identity")
    assert player_identity["states"]["IDENTITY_RESOLVED"] is False
    assert player_identity["states"]["REVIEW_REQUIRED"] is True
    assert player_identity["states"]["PRODUCT_READY"] is True

def test_player_identity_collapses_repeated_fixture_observations() -> None:
    player_rows = [
        {
            "element": "1",
            "player_code": "1001",
            "team_code": "10",
            "minutes": "90",
            "starts": "1",
        },
        {
            "element": "1",
            "player_code": "1001",
            "team_code": "10",
            "minutes": "72",
            "starts": "1",
        },
    ]

    identities = module.build_player_identities(
        player_rows,
        season="2026-27",
        bridge_candidates={"1001": {"9001"}},
        bridge_seasons={"1001": {"2025-26"}},
        registered_source_player_ids={"9001"},
        source_commit="abc123",
        source_path="_merged/players/2026-27_all_players_gw.csv",
        source_sha256="deadbeef",
    )

    assert len(identities) == 1
    assert identities[0]["fpl_element"] == "1"
    assert identities[0]["fpl_player_code"] == "1001"


def test_player_identity_rejects_element_reuse_for_different_player_code() -> None:
    player_rows = [
        {"element": "1", "player_code": "1001", "team_code": "10"},
        {"element": "1", "player_code": "9999", "team_code": "10"},
    ]

    with pytest.raises(module.MaterialisationError, match="Inconsistent FPL player identity"):
        module.build_player_identities(
            player_rows,
            season="2026-27",
            bridge_candidates={},
            bridge_seasons={},
            registered_source_player_ids=set(),
            source_commit="abc123",
            source_path="_merged/players/2026-27_all_players_gw.csv",
            source_sha256="deadbeef",
        )
