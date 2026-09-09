from __future__ import annotations

import api.fixture_evidence as route


def test_optional_participation_enrichment_cannot_suppress_fixture_events(monkeypatch) -> None:
    base = {
        "status": "AVAILABLE",
        "events": [
            {
                "event_id": "goal-1",
                "type": "goal",
                "side": "away",
                "minute": "72",
                "primary_player": {"name": "Away Scorer"},
            }
        ],
        "lineup": [],
        "formation": {},
        "managers": {"status": "UNAVAILABLE", "items": []},
        "metadata": {"ground": "Example Ground"},
        "limitations": [],
        "provenance": {"source_family": "pulselive_match"},
    }

    monkeypatch.setattr(route, "source_fixture_evidence", lambda season, fixture_id: base)

    def fail_enrichment(season: str, fixture_id: str) -> dict:
        raise RuntimeError("optional Player-Match enrichment unavailable")

    monkeypatch.setattr(route, "fixture_research_result", fail_enrichment)

    result = route.get_fixture_evidence("2025-26", "380")

    assert result["status"] == "AVAILABLE"
    assert result["events"] == base["events"]
    assert result["metadata"] == base["metadata"]
    assert result["provenance"]["participation_enrichment"]["status"] == "UNAVAILABLE"
    assert result["provenance"]["participation_enrichment"]["optional"] is True
    assert any("participation enrichment" in note for note in result["limitations"])
