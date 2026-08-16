import player_identity_registry


def test_module_shape():
    assert hasattr(player_identity_registry, "build_registry")
    assert hasattr(player_identity_registry, "write_registry")
    assert player_identity_registry.FIELDS[0] == "season"


def test_reject_review_rows(monkeypatch):
    monkeypatch.setattr(
        player_identity_registry.player_identity_crosswalk,
        "summarize",
        lambda: {"review_rows": 1, "confirmed": []},
    )
    try:
        player_identity_registry.build_registry()
    except ValueError as exc:
        assert "review rows remain" in str(exc)
    else:
        raise AssertionError("review rows must block registry promotion")


if __name__ == "__main__":
    tests = [test_module_shape, test_reject_review_rows]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"PLAYER IDENTITY REGISTRY TESTS: {len(tests)}/{len(tests)}")
