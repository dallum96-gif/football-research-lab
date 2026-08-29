from __future__ import annotations

import json
from pathlib import Path

import pytest

import pulselive_materialization as materialization
from pulselive_live import PulseLiveRequestError


def _package(source_match_id: str) -> dict:
    retrieved_at = "2026-08-29T00:00:00+00:00"

    def resource(name: str, payload: object) -> dict:
        return {
            "endpoint": f"https://example.test/{name}/{source_match_id}",
            "retrieved_at": retrieved_at,
            "status_code": 200,
            "headers": {},
            "payload": payload,
        }

    return {
        "source": "Premier League / PulseLive SDP",
        "source_match_id": source_match_id,
        "retrieved_at": retrieved_at,
        "resources": {
            "match": resource("match", {
                "matchId": source_match_id,
                "homeTeam": {"id": "1"},
                "awayTeam": {"id": "2"},
            }),
            "events": resource("events", {
                "homeTeam": {"goals": [], "cards": [], "subs": []},
                "awayTeam": {"goals": [], "cards": [], "subs": []},
            }),
            "lineups": resource("lineups", {
                "home_team": {
                    "teamId": "1",
                    "players": [{"id": "11", "firstName": "Home", "lastName": "Player"}],
                    "formation": {"formation": "4-3-3", "lineup": [["11"]], "subs": []},
                    "managers": [],
                },
                "away_team": {
                    "teamId": "2",
                    "players": [{"id": "21", "firstName": "Away", "lastName": "Player"}],
                    "formation": {"formation": "4-4-2", "lineup": [["21"]], "subs": []},
                    "managers": [],
                },
            }),
            "stats": resource("stats", [
                {"side": "Home", "teamId": "1", "stats": {"goals": 0}},
                {"side": "Away", "teamId": "2", "stats": {"goals": 0}},
            ]),
            "commentary": resource("commentary", {"pagination": {}, "data": []}),
        },
    }


def _relationship(source_match_id: str) -> dict:
    return {
        "source_match_id": source_match_id,
        "relationship_contract": "canonical_fixture_to_source_match",
        "relationship_status": "VERIFIED",
        "resolution_basis": "CANONICAL_FIXTURE",
        "fixture_correction": None,
    }


def test_successful_materialization_is_atomic_and_existing_valid_snapshot_is_skipped(tmp_path: Path) -> None:
    calls = []

    def fetcher(source_match_id: str, **options):
        calls.append((source_match_id, options))
        return _package(source_match_id)

    first = materialization.materialize_fixture(
        "2016-17",
        "8",
        root=tmp_path,
        fetcher=fetcher,
        resolved=_relationship("855173"),
        request_interval_seconds=0,
    )
    second = materialization.materialize_fixture(
        "2016-17",
        "8",
        root=tmp_path,
        fetcher=fetcher,
        resolved=_relationship("855173"),
        request_interval_seconds=0,
    )

    assert first["status"] == "MATERIALIZED"
    assert second["status"] == "SKIPPED"
    assert len(calls) == 1
    path = Path(first["snapshot_path"])
    captured = json.loads(path.read_text(encoding="utf-8"))
    assert captured["materialization"]["status"] == "COMPLETE"
    assert captured["frl_context"]["fixture_id"] == "8"
    assert not list(path.parent.glob("*.tmp"))


def test_bulk_records_failure_continues_and_can_retry_only_failures(monkeypatch, tmp_path: Path) -> None:
    relationships = {"1": "1001", "2": "1002"}
    monkeypatch.setattr(
        materialization,
        "resolve_source_match",
        lambda season, fixture_id: _relationship(relationships[str(fixture_id)]),
    )

    def first_fetch(source_match_id: str, **options):
        if source_match_id == "1001":
            raise PulseLiveRequestError(
                "temporary failure",
                endpoint="https://example.test/events/1001",
                status_code=503,
                transient=True,
            )
        return _package(source_match_id)

    fixtures = [
        {"season": "2020-21", "fixture_id": "1"},
        {"season": "2020-21", "fixture_id": "2"},
    ]
    first = materialization.materialize_many(
        fixtures,
        root=tmp_path,
        fetcher=first_fetch,
        fixture_interval_seconds=0,
        request_interval_seconds=0,
    )
    state = materialization.load_materialization_state(tmp_path)
    failed = materialization.failed_fixture_keys(state)

    assert first["counts"] == {"MATERIALIZED": 1, "SKIPPED": 0, "FAILED": 1}
    assert failed == {"2020-21/1"}
    assert state["fixtures"]["2020-21/1"]["status_code"] == 503

    retry_rows = [row for row in fixtures if f"{row['season']}/{row['fixture_id']}" in failed]
    retried = materialization.materialize_many(
        retry_rows,
        root=tmp_path,
        fetcher=lambda source_match_id, **options: _package(source_match_id),
        fixture_interval_seconds=0,
        request_interval_seconds=0,
    )

    assert retried["counts"] == {"MATERIALIZED": 1, "SKIPPED": 0, "FAILED": 0}
    assert materialization.failed_fixture_keys(materialization.load_materialization_state(tmp_path)) == set()
    assert materialization.snapshot_target(tmp_path, "1002").is_file()


def test_failed_atomic_replace_leaves_no_snapshot_or_temporary_file(monkeypatch, tmp_path: Path) -> None:
    target = materialization.snapshot_target(tmp_path, "855173")

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(materialization.os, "replace", fail_replace)

    with pytest.raises(OSError, match="simulated replace failure"):
        materialization.materialize_fixture(
            "2016-17",
            "8",
            root=tmp_path,
            fetcher=lambda source_match_id, **options: _package(source_match_id),
            resolved=_relationship("855173"),
            request_interval_seconds=0,
        )

    assert not target.exists()
    assert target.parent.is_dir()
    assert not list(target.parent.glob("*.tmp"))
