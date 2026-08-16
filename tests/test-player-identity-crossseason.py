import player_identity_crossseason_audit


def test_module_shape():
    assert hasattr(player_identity_crossseason_audit, "build_anchor_maps")
    assert hasattr(player_identity_crossseason_audit, "audit_crossseason")


def test_anchor_maps_shape():
    report = {
        "seasons": {
            "2025-26": {
                "exact": [
                    {
                        "fpl_name": "Bukayo Saka",
                        "fpl_player_code": "123",
                        "source_player_id": "934235",
                        "team_code": "3",
                    }
                ],
                "missing": [],
            }
        }
    }
    source_to_names, source_to_teams, fpl_to_source = player_identity_crossseason_audit.build_anchor_maps(report)
    assert source_to_names["934235"] == {"bukayo saka"}
    assert source_to_teams["934235"] == {"3"}
    assert fpl_to_source[("2025-26", "123")] == {"934235"}


def test_crossseason_shape():
    report = {
        "seasons": {
            "2025-26": {
                "exact": [],
                "missing": [
                    {
                        "name": "bukayo saka",
                        "team_code": "3",
                        "fpl_ids": ["123"],
                    }
                ],
            }
        }
    }
    result = player_identity_crossseason_audit.audit_crossseason(report)
    assert set(result) == {
        "anchored_source_ids",
        "alias_candidates",
        "unresolved",
        "crossseason_name_variants",
    }


if __name__ == "__main__":
    tests = [test_module_shape, test_anchor_maps_shape, test_crossseason_shape]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"PLAYER IDENTITY CROSS-SEASON TESTS: {len(tests)}/{len(tests)}")
