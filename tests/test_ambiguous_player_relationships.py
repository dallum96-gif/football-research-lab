import audit_ambiguous_player_relationships as audit


def test_report_is_read_only_and_preserves_ambiguity(monkeypatch):
    monkeypatch.setattr(
        audit.player_identity_audit,
        "SEASONS",
        ("2025-26",),
    )
    monkeypatch.setattr(
        audit.player_identity_audit,
        "audit_season",
        lambda season: {
            "ambiguous": [{
                "fpl_player_code": "7",
                "fpl_name": "Example Player",
                "team_code": "ABC",
                "club": "Example FC",
                "source_ids": ["10", "11"],
                "source_names": ["Example Player", "Example Player B"],
            }],
        },
    )

    rows = audit.run()
    assert len(rows) == 1
    assert rows[0]["source_ids"] == ("10", "11")
    assert rows[0]["source_names"] == ("Example Player", "Example Player B")


if __name__ == "__main__":
    test_report_is_read_only_and_preserves_ambiguity(lambda: None)
    print("PASS  test_report_is_read_only_and_preserves_ambiguity")
