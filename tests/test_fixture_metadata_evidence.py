from __future__ import annotations

import fixture_metadata_evidence as metadata


def test_pulselive_match_metadata_supplements_historical_fixture_metadata(monkeypatch):
    monkeypatch.setattr(
        metadata,
        "resolve_source_match",
        lambda season, fixture_id: {
            "source_match_id": "999",
            "home": {"referee": "Historical Referee"},
            "away": {},
        },
    )
    monkeypatch.setattr(
        metadata,
        "fixture_metadata",
        lambda season, fixture_id: {
            "source_match_id": "999",
            "ground": None,
            "attendance": None,
        },
    )
    monkeypatch.setattr(
        metadata,
        "load_snapshot",
        lambda source_match_id: (
            {
                "resources": {
                    "match": {
                        "payload": {
                            "matchId": "999",
                            "ground": {"name": "Selhurst Park"},
                            "attendance": 25192,
                        }
                    }
                }
            },
            "/tmp/match-999/snapshot.json",
        ),
    )

    result = metadata.fixture_metadata_result("2025-26", "123")

    assert result["ground"] == "Selhurst Park"
    assert result["attendance"] == 25192
    assert result["referee"] == "Historical Referee"
    assert result["metadata_provenance"]["pulselive_match_snapshot"] is True


def test_match_payload_referee_is_used_only_when_explicit(monkeypatch):
    monkeypatch.setattr(
        metadata,
        "resolve_source_match",
        lambda season, fixture_id: {
            "source_match_id": "999",
            "home": {},
            "away": {},
        },
    )
    monkeypatch.setattr(
        metadata,
        "fixture_metadata",
        lambda season, fixture_id: {
            "source_match_id": "999",
            "ground": None,
            "attendance": None,
        },
    )
    monkeypatch.setattr(
        metadata,
        "load_snapshot",
        lambda source_match_id: (
            {
                "resources": {
                    "match": {
                        "payload": {
                            "matchId": "999",
                            "ground": {"name": "Example Ground"},
                            "attendance": 42000,
                            "officials": [
                                {"role": "Assistant", "name": "Assistant Official"},
                                {"role": "Referee", "name": "Main Official"},
                            ],
                        }
                    }
                }
            },
            "/tmp/match-999/snapshot.json",
        ),
    )

    result = metadata.fixture_metadata_result("2025-26", "123")

    assert result["referee"] == "Main Official"


def test_missing_referee_remains_unknown(monkeypatch):
    monkeypatch.setattr(
        metadata,
        "resolve_source_match",
        lambda season, fixture_id: {
            "source_match_id": "999",
            "home": {},
            "away": {},
        },
    )
    monkeypatch.setattr(
        metadata,
        "fixture_metadata",
        lambda season, fixture_id: {
            "source_match_id": "999",
            "ground": "Existing Ground",
            "attendance": 10000,
        },
    )
    monkeypatch.setattr(metadata, "load_snapshot", lambda source_match_id: (None, None))

    result = metadata.fixture_metadata_result("2025-26", "123")

    assert result["ground"] == "Existing Ground"
    assert result["attendance"] == 10000
    assert result["referee"] is None
