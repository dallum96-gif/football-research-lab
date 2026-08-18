import player_identity_crosswalk


def test_normalize_name():
    assert player_identity_crosswalk.normalize_name("Miloš Kerkez") == "milos kerkez"
    assert player_identity_crosswalk.normalize_name("Gabriel Magalhães") == "gabriel magalhaes"


def test_crosswalk_shape():
    result = player_identity_crosswalk.summarize()
    assert set(result) == {
        "candidate_rows",
        "confirmed_rows",
        "review_rows",
        "source_ids_spanning_seasons",
        "confirmed",
        "review",
        "source_multi",
    }


if __name__ == "__main__":
    tests = [test_normalize_name, test_crosswalk_shape]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"PLAYER IDENTITY CROSSWALK TESTS: {len(tests)}/{len(tests)}")
