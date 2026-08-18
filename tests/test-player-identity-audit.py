import player_identity_audit


def test_name_normalization():
    assert player_identity_audit.normalize_name("Álvaro Odriozola") == "alvaro odriozola"
    assert player_identity_audit.normalize_name(" Gabriel  Jesus ") == "gabriel jesus"
    assert player_identity_audit.normalize_name("O'Riley") == "oriley"


def test_source_seasons_available():
    seasons = set(player_identity_audit.SEASONS)
    assert {"2016-17", "2019-20", "2025-26"}.issubset(seasons)


def test_audit_shape():
    report = player_identity_audit.run_audit()
    assert "seasons" in report
    assert "totals" in report
    assert set(report["totals"]) == {"exact", "missing", "ambiguous"}


TESTS = [
    test_name_normalization,
    test_source_seasons_available,
    test_audit_shape,
]


if __name__ == "__main__":
    passed = 0
    for test in TESTS:
        try:
            test()
            print(f"PASS  {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL  {test.__name__}: {exc}")

    print()
    print(f"PLAYER IDENTITY AUDIT TESTS: {passed}/{len(TESTS)}")
    if passed != len(TESTS):
        raise SystemExit(1)
