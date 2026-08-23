import audit_unresolved_player_match_evidence as audit


def test_module_shape():
    assert hasattr(audit, "classify")
    assert hasattr(audit, "print_report")


def test_direct_crosswalk_maps_shape(monkeypatch):
    monkeypatch.setattr(
        audit.player_identity_crosswalk,
        "build_crosswalk_candidates",
        lambda: [
            {
                "season": "2025-26",
                "element": "123",
                "source_player_id": "934235",
            }
        ],
    )
    pair_to_sources, source_to_pairs = audit._direct_crosswalk_maps()
    assert pair_to_sources[("2025-26", "123")] == {"934235"}
    assert source_to_pairs["934235"] == {("2025-26", "123")}


def test_classification_precedence(monkeypatch):
    rows_by_season = {
        "2025-26": [
            {"playerId": "1", "playerName": "One"},
            {"playerId": "2", "playerName": "Two"},
            {"playerId": "3", "playerName": "Three"},
            {"playerId": "4", "playerName": "Four"},
        ]
    }

    monkeypatch.setattr(audit, "_source_rows_by_season", lambda: rows_by_season)
    monkeypatch.setattr(
        audit,
        "_direct_crosswalk_maps",
        lambda: (
            {("2025-26", "11"): {"3"}},
            {"3": {("2025-26", "11")}},
        ),
    )
    monkeypatch.setattr(
        audit,
        "_research_closure_map",
        lambda _pairs: {"1": {"Player One"}},
    )
    monkeypatch.setattr(
        audit,
        "_source_continuity",
        lambda _rows: (
            {
                "1": {"2025-26"},
                "2": {"2024-25", "2025-26"},
                "3": {"2025-26"},
                "4": {"2025-26"},
            },
            {},
            {},
        ),
    )
    monkeypatch.setattr(
        audit.player_identity_audit,
        "run_audit",
        lambda: {
            "seasons": {
                "2025-26": {
                    "exact": [],
                    "missing": [],
                }
            }
        },
    )
    monkeypatch.setattr(
        audit.player_identity_crossseason_audit,
        "audit_crossseason",
        lambda _report: {
            "confirmed": [{
                "source_player_id": "2",
                "season": "2025-26",
                "fpl_name": "Two",
                "fpl_player_codes": ["22"],
                "team_code": "3",
            }]
        },
    )

    result = audit.classify()
    categories = {
        row["source_player_id"]: row["evidence_category"]
        for row in result["records"]
    }
    assert categories["1"] == "UNRESOLVED_BUT_UNIQUE_RESEARCH_IDENTITY"
    assert categories["2"] == "UNRESOLVED_WITH_CROSS_SEASON_ANCHOR"
    assert categories["3"] == "UNRESOLVED_WITH_DIRECT_CROSSWALK_EVIDENCE"
    assert categories["4"] == "UNRESOLVED_NO_CURRENT_IDENTITY_PATH"


if __name__ == "__main__":
    test_module_shape()
    print("PASS test_module_shape")
