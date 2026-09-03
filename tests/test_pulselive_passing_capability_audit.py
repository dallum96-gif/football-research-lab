from __future__ import annotations

import json
from pathlib import Path

from scripts.audit_pulselive_passing_capability import audit_archive, discover_snapshot


def _write_snapshot(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_discover_snapshot_finds_passing_like_fields_by_resource(tmp_path: Path) -> None:
    path = tmp_path / "match-123" / "snapshot.json"
    _write_snapshot(
        path,
        {
            "fixture": {"id": "123"},
            "resources": {
                "stats": {
                    "payload": {
                        "home": {
                            "totalPass": 520,
                            "accuratePass": 468,
                            "accurateThroughBall": 4,
                            "possessionPercentage": 58.2,
                        }
                    }
                },
                "lineups": {"payload": {"homeTeam": {"players": []}}},
            },
        },
    )

    result = discover_snapshot(path)

    assert result["source_match_id"] == "123"
    assert "stats" in result["passing_resources"]
    assert "home.totalPass" in result["passing_resources"]["stats"]
    assert "home.accuratePass" in result["passing_resources"]["stats"]
    assert "home.accurateThroughBall" in result["passing_resources"]["stats"]
    assert "home.possessionPercentage" in result["passing_resources"]["stats"]
    assert "lineups" not in result["passing_resources"]


def test_audit_archive_is_read_only_and_reports_union_of_passing_paths(tmp_path: Path) -> None:
    first = tmp_path / "match-1" / "snapshot.json"
    second = tmp_path / "match-2" / "snapshot.json"
    _write_snapshot(
        first,
        {"resources": {"teamStats": {"payload": {"totalPass": 400}}}},
    )
    _write_snapshot(
        second,
        {"resources": {"playerStats": {"payload": [{"keyPass": 3, "totalCross": 5}]}}},
    )

    before = {path: path.read_bytes() for path in (first, second)}
    result = audit_archive(tmp_path)
    after = {path: path.read_bytes() for path in (first, second)}

    assert result["snapshot_files_scanned"] == 2
    assert result["snapshots_with_passing_fields"] == 2
    assert "teamStats" in result["passing_resource_names"]
    assert "playerStats" in result["passing_resource_names"]
    assert "totalPass" in result["passing_key_paths"]
    assert "[].keyPass" in result["passing_key_paths"]
    assert "[].totalCross" in result["passing_key_paths"]
    assert before == after
