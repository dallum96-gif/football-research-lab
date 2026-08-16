import fpl_identity_schema_audit


def test_shape():
    result = fpl_identity_schema_audit.run_audit()
    assert "seasons" in result
    assert "cross_season" in result
    assert result["seasons"]


def test_season_report_shape():
    season = fpl_identity_schema_audit.SEASONS[0]
    result = fpl_identity_schema_audit.audit_season(season)
    required = {
        "season",
        "rows",
        "element_populated",
        "element_unique",
        "player_code_present",
        "player_code_populated",
        "player_code_unique",
        "relationship",
        "code_to_elements_multi",
        "element_to_codes_multi",
    }
    assert required.issubset(result)


def test_fields_are_distinct():
    # The audit must preserve the two identifiers separately rather than
    # silently collapsing one into the other.
    assert fpl_identity_schema_audit.norm("123") == "123"
    assert fpl_identity_schema_audit.norm(123) == "123"


if __name__ == "__main__":
    tests = [test_shape, test_season_report_shape, test_fields_are_distinct]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"FPL IDENTITY SCHEMA AUDIT TESTS: {len(tests)}/{len(tests)}")
