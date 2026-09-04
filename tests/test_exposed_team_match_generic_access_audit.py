from __future__ import annotations

from types import SimpleNamespace

from scripts import audit_exposed_team_match_generic_access as audit


def _reconciliation():
    return {
        "rows": [
            {
                "source_field": "backwardPass",
                "raw_path": "[].stats.backwardPass",
                "raw_logical_family": "Passing",
                "reconciliation_status": "EXISTING_EXPOSED",
                "existing_first_seen_season": "2016-17",
                "existing_last_seen_season": "2025-26",
                "existing_coverage_class": "CORE_DECADE",
            },
            {
                "source_field": "wonContest",
                "raw_path": "[].stats.wonContest",
                "raw_logical_family": "Defending & duels",
                "reconciliation_status": "EXISTING_SOURCE_FIELD_UNCATALOGUED",
            },
        ]
    }


def test_audit_only_checks_exposed_reconciled_team_stat_fields(monkeypatch):
    monkeypatch.setattr(audit, "build_reconciliation", lambda path: _reconciliation())
    monkeypatch.setattr(
        audit.research_access,
        "discover",
        lambda **kwargs: {
            "results": [
                {"variable": "backwardPass", "status": "exposed"},
                {"variable": "wonContest", "status": "UNCATALOGUED"},
            ]
        },
    )
    monkeypatch.setattr(
        audit,
        "_observed_fixture",
        lambda field, **kwargs: ("2025-26", "100") if field == "backwardPass" else None,
    )
    monkeypatch.setattr(
        audit,
        "variable_definition",
        lambda *args, **kwargs: SimpleNamespace(status="exposed"),
    )
    monkeypatch.setattr(
        audit,
        "resolve_variable",
        lambda *args, **kwargs: {
            "results": [
                {"source_field": "backwardPass", "value": 100},
                {"source_field": "backwardPass", "value": 110},
            ]
        },
    )

    rows = audit.audit_rows(audit.DEFAULT_RAW_CATALOGUE)

    assert len(rows) == 1
    assert rows[0]["source_field"] == "backwardPass"
    assert rows[0]["generic_access_status"] == "PASS"
    assert rows[0]["query_status"] == "PASS"
    assert rows[0]["observed_values"] == 2


def test_audit_fails_when_discovery_does_not_reflect_exposed_status(monkeypatch):
    monkeypatch.setattr(audit, "build_reconciliation", lambda path: _reconciliation())
    monkeypatch.setattr(
        audit.research_access,
        "discover",
        lambda **kwargs: {
            "results": [{"variable": "backwardPass", "status": "UNCATALOGUED"}]
        },
    )
    monkeypatch.setattr(
        audit,
        "_observed_fixture",
        lambda field, **kwargs: ("2025-26", "100"),
    )
    monkeypatch.setattr(
        audit,
        "variable_definition",
        lambda *args, **kwargs: SimpleNamespace(status="exposed"),
    )
    monkeypatch.setattr(
        audit,
        "resolve_variable",
        lambda *args, **kwargs: {
            "results": [{"source_field": "backwardPass", "value": 100}]
        },
    )

    rows = audit.audit_rows(audit.DEFAULT_RAW_CATALOGUE)

    assert rows[0]["generic_access_status"] == "FAIL"
    assert rows[0]["query_status"] == "PASS"
    assert rows[0]["discoverable_as_exposed"] is False


def test_audit_fails_closed_on_query_exception(monkeypatch):
    monkeypatch.setattr(audit, "build_reconciliation", lambda path: _reconciliation())
    monkeypatch.setattr(
        audit.research_access,
        "discover",
        lambda **kwargs: {
            "results": [{"variable": "backwardPass", "status": "exposed"}]
        },
    )
    monkeypatch.setattr(
        audit,
        "_observed_fixture",
        lambda field, **kwargs: ("2025-26", "100"),
    )
    monkeypatch.setattr(
        audit,
        "variable_definition",
        lambda *args, **kwargs: SimpleNamespace(status="exposed"),
    )

    def _boom(*args, **kwargs):
        raise ValueError("broken generic route")

    monkeypatch.setattr(audit, "resolve_variable", _boom)

    rows = audit.audit_rows(audit.DEFAULT_RAW_CATALOGUE)

    assert rows[0]["generic_access_status"] == "FAIL"
    assert rows[0]["query_status"] == "ERROR"
    assert "broken generic route" in rows[0]["query_error"]
